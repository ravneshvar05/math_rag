
import sys
import os
import time
import numpy as np
from app.pipeline import MathRAGPipeline
from retrieval.hybrid_retriever import HybridRetriever

def run_local_benchmark():
    print("Initializing Local MathRAG Pipeline...")
    pipeline = MathRAGPipeline()
    
    # Initialize components explicitly
    print("Loading indices...")
    pipeline._init_query_components()
    
    if not pipeline.retriever:
        print("Error: Retriever could not be initialized.")
        return

    # Queries from the Colab Benchmark
    QUERIES = [
        "What are the questions in Exercise 3.1?",
        "Find the radian measures: (i) 25 degrees (ii) -47 degrees 30 minutes",
        "How many rotations does a wheel make if it turns 360 times in one minute?",
        "Show Example 13",
        "Prove that (sin x + sin 3x) / (cos x + cos 3x) = tan 2x",
        "What is the relation between radian and real numbers?",
        "Find the degree measure of 11/16 radians",
        "A pendulum swings through an angle of radian if its length is 75 cm"
    ]
    
    results = []
    total_score = 0
    
    print(f"\nRunning Latency & Retrieval Benchmark on {len(QUERIES)} queries...")
    
    for query in QUERIES:
        print(f"  - Query: {query}")
        start_t = time.time()
        
        # We use the pipeline's retriever directly to get scores
        # Returns List[RetrievalResult] or List[Tuple[ContentChunk, float]] depending on version
        # Let's check the return type at runtime
        try:
             # pipeline.retriever is HybridRetriever
            retrieval_results = pipeline.retriever.retrieve(query, top_k=1)
            
            elapsed = time.time() - start_t
            
            if retrieval_results:
                # Based on previous code inspection, search returns list of results
                # Let's handle both object and tuple
                top_result = retrieval_results[0]
                
                if hasattr(top_result, 'chunk'): # Result object
                    chunk = top_result.chunk
                    score = top_result.score
                elif isinstance(top_result, tuple) or isinstance(top_result, list): # Tuple
                    chunk = top_result[0]
                    score = top_result[1]
                else:
                    # Direct chunk object?
                    chunk = top_result
                    score = getattr(top_result, 'score', 0.0)
                
                # Get text content
                text = getattr(chunk, 'text_content', str(chunk))
                
                results.append({
                    "query": query,
                    "score": score,
                    "text": text,
                    "time": elapsed
                })
                total_score += score
            else:
                results.append({
                    "query": query,
                    "score": 0.0,
                    "text": "NO RESULTS FOUND",
                    "time": elapsed
                })
        except Exception as e:
            print(f"    Error querying: {e}")
            results.append({
                "query": query,
                "score": 0.0,
                "text": f"ERROR: {e}",
                "time": 0.0
            })
            
    avg_score = total_score / len(QUERIES) if QUERIES else 0
    
    # Generate Report
    report_path = "local_benchmark_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Local MathRAG Benchmark Report\n\n")
        f.write(f"**Date:** {time.ctime()}\n")
        f.write("**Strategy:** Custom `StructureAwareChunker` + Hybrid Retrieval (BGE-Large + BM25)\n")
        f.write(f"**Average Hybrid Score:** {avg_score:.4f} (Note: Hybrid scores are RRF-weighted, not direct cosine)\n\n")
        
        f.write("## Detailed Results\n\n")
        f.write("| Query | Score | Latency (s) | Preview |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        
        for res in results:
            preview = res['text'][:150].replace('\n', ' ').replace('|', '') + "..."
            f.write(f"| {res['query']} | **{res['score']:.4f}** | {res['time']:.2f} | {preview} |\n")
            
        f.write("\n\n## Full Retrieval Content (Top 1)\n")
        for i, res in enumerate(results):
            f.write(f"### {i+1}. {res['query']}\n")
            f.write(f"- **Score:** {res['score']:.4f}\n")
            f.write(f"- **Latency:** {res['time']:.4f}s\n")
            f.write(f"- **Retrieved Chunk:**\n")
            f.write(f"```text\n{res['text']}\n```\n")
            f.write("---\n")
            
    print(f"\n✓ Benchmark complete! Report saved to {report_path}")
    print(f"  > Avg Score: {avg_score:.4f}")

if __name__ == "__main__":
    run_local_benchmark()
