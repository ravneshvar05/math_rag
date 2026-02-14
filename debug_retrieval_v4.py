import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path.cwd()))

from app.pipeline import MathRAGPipeline
from utils.logging import get_logger

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = get_logger(__name__)

def debug_full_search():
    print("--- Debugging Full Search for 'exercise 3.3 questions only' ---")
    
    # Initialize pipeline but we only need retrieval components
    pipeline = MathRAGPipeline()
    
    # Manually init retrieval components to avoid loading LLM if possible
    # But pipeline.id() does it all.
    # Let's call pipeline._init_query_components()
    try:
        pipeline._init_query_components()
    except Exception as e:
        print(f"Init failed (likely missing API key or model): {e}")
        # We might need to mock LLM client if we don't have key in env
        # assuming env is set based on previous context
        
    query = "give me excercise 3.3 questions only"
    
    # Perform search using the retrieval pipeline directly
    # Need to check if pipeline.retrieval_pipeline is initialized
    if not pipeline.retrieval_pipeline:
         # Try to force init retrieval if LLM failed
         from retrieval.hybrid_retriever import HybridRetriever, QueryClassifier, RetrievalPipeline
         
         if not pipeline.retriever:
             pipeline._init_indexing_components() # Ensure stores are loaded
             # Re-init retriever manually if needed or just use existing
             # A lot of dependencies. Let's just create a temporary retrieving pipeline
             pass
    if pipeline.retrieval_pipeline:
        results = pipeline.retrieval_pipeline.search(query, top_k=5)
        
        print(f"\nFound {len(results)} chunks:")
        for i, res in enumerate(results):
            chunk = res.chunk
            print(f"\n[Rank {i+1}] Score: {res.score:.4f}")
            print(f"Chunk ID: {chunk.chunk_id}")
            print(f"Section: {chunk.section_name}")
            print(f"Text Preview: {chunk.text_content[:100]}...")
            
            if chunk.images:
                print(f"Linked Images ({len(chunk.images)}):")
                for img in chunk.images:
                    print(f"  - {img.image_path}")
            else:
                print("No Linked Images")
    else:
        print("Retrieval pipeline not initialized.")

if __name__ == "__main__":
    debug_full_search()
