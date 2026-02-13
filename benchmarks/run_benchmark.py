
import os
import sys
import time
import json
import numpy as np
import fitz # PyMuPDF
import torch
import gc
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chunking.structure_aware_chunker import StructureAwareChunker
from extraction.pdf_extractor import PDFExtractor
from utils.logging import get_logger

# Force UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

CACHE_DIR = "benchmarks/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Mock Config for Chunker
def get_chunker_config(chunk_size):
    return {
        'min_tokens': 100,
        'max_tokens': chunk_size,
        'overlap_tokens': 50,
        'preserve_units': ['proof', 'example', 'exercise']
    }

class UnstructuredHybridWrapper:
    """Wrapper for Hybrid Unstructured Partitioning (Fitz -> Unstructured Elements)."""
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size
        
    def chunk(self, pdf_path):
        try:
            from unstructured.documents.elements import Text, Title
            from unstructured.chunking.title import chunk_by_title
            
            doc = fitz.open(pdf_path)
            elements = []
            
            for page in doc:
                blocks = page.get_text("dict")["blocks"]
                for b in blocks:
                    if "lines" in b:
                        for line in b["lines"]:
                            text = " ".join([span["text"] for span in line["spans"]]).strip()
                            if not text: continue
                            
                            # Simple heuristic for Title vs Text
                            if len(text) < 50 and (text.isupper() or not text.endswith('.')):
                                elements.append(Title(text=text))
                            else:
                                elements.append(Text(text=text))
            
            # Close doc to free memory
            doc.close()
                                
            # Chunking (approx 4 chars per token for max_characters)
            chunks = chunk_by_title(elements, max_characters=self.chunk_size * 4)
            return [str(c) for c in chunks]
            
        except ImportError:
            print("Unstructured library not fully installed.")
            return []
        except Exception as e:
            print(f"Unstructured Error: {e}")
            return []

def get_cached_chunks(strategy, size, pdf_name):
    cache_file = os.path.join(CACHE_DIR, f"{strategy}_{size}_{pdf_name}.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_cached_chunks(chunks, strategy, size, pdf_name):
    cache_file = os.path.join(CACHE_DIR, f"{strategy}_{size}_{pdf_name}.json")
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

def clear_memory():
    """Clear RAM and VRAM."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    time.sleep(2)

def run_benchmark():
    pdf_name = "Mathematics-11 1-43-75.pdf"
    pdf_path = os.path.join("data/raw", pdf_name)
    
    if not os.path.exists(pdf_path):
        files = [f for f in os.listdir("data/raw") if f.endswith(".pdf")]
        if files:
            pdf_name = files[0]
            pdf_path = os.path.join("data/raw", pdf_name)
        else:
            print("No PDF found to benchmark.")
            return

    # Configuration
    MODELS = [
        "BAAI/bge-large-en-v1.5",
        "nomic-ai/nomic-embed-text-v1.5"
    ]
    CHUNK_SIZES = [500, 1000]
    STRATEGIES = ["StructureAware", "Unstructured"]
    
    # REAL Math Questions
    QUERIES = [
        "Find the radian measures corresponding to the following degree measures: 25 degrees",
        "Find the value of sin 31pi/3",
        "Prove that: (sin x + sin 3x) / (cos x + cos 3x) = tan 2x",
        "Value of tan 13pi/12",
        "show the example 13",
        "What are the questions in Exercise 3.1?",
        "Convert 520 degrees into radian measure.",
        "Find the value of cos(-1710 degrees).",
        "What is the relation between radian and real numbers?"
    ]

    results_file = "benchmark_results.txt"
    with open(results_file, "w", encoding='utf-8') as f:
        f.write(f"Benchmark Request: {time.ctime()}\n")
        f.write(f"Questions Tested:\n")
        for i, q in enumerate(QUERIES):
            f.write(f"  {i+1}. {q}\n")
        f.write("\n")

    print(f"Starting Benchmark on {pdf_name}...", flush=True)
    device = 'cpu'
    print(f"Forced Device: {device.upper()} (Stability Mode)", flush=True)

    for strategy in STRATEGIES:
        for size in CHUNK_SIZES:
            print(f"\n--- Strategy: {strategy} | Size: {size} ---", flush=True)
            
            chunks_text = get_cached_chunks(strategy, size, pdf_name)
            
            if chunks_text is None:
                start_time = time.time()
                if strategy == "StructureAware":
                    extractor = PDFExtractor(pdf_path, "benchmarks/temp")
                    data = extractor.extract_all()
                    chunker = StructureAwareChunker(get_chunker_config(size))
                    chunk_objs = chunker.chunk_document(data['pages'], "bench_doc", "11")
                    chunks_text = [c.text_content for c in chunk_objs]
                    
                elif strategy == "Unstructured":
                    wrapper = UnstructuredHybridWrapper(size)
                    chunks_text = wrapper.chunk(pdf_path)
                
                build_time = time.time() - start_time
                save_cached_chunks(chunks_text, strategy, size, pdf_name)
                print(f"Chunking completed in {build_time:.2f}s (Saved to Cache)", flush=True)
            else:
                build_time = 0.0
                print("Loaded chunks from Cache.", flush=True)

            num_chunks = len(chunks_text)
            if num_chunks == 0:
                print("No chunks generated.", flush=True)
                continue

            avg_len = np.mean([len(c) for c in chunks_text])
            
            # Evaluate Models sequentially to save memory
            for model_name in MODELS:
                print(f"  Evaluating Model: {model_name}", flush=True)
                model = None
                try:
                    # 1. Load Model
                    print(f"    Loading {model_name}...", flush=True)
                    model = SentenceTransformer(model_name, trust_remote_code=True, device=device)
                    
                    # 2. Embed and Evaluate
                    start_retrieval = time.time()
                    try:
                        chunk_embeddings = model.encode(chunks_text, normalize_embeddings=True, show_progress_bar=False)
                        query_embeddings = model.encode(QUERIES, normalize_embeddings=True, show_progress_bar=False)
                    except Exception as e_mem:
                        if "OUT OF MEMORY" in str(e_mem).upper() or "CUDA" in str(e_mem).upper():
                            print(f"    CUDA Error: {e_mem}. Falling back to CPU...", flush=True)
                            model.to('cpu')
                            chunk_embeddings = model.encode(chunks_text, normalize_embeddings=True, show_progress_bar=False)
                            query_embeddings = model.encode(QUERIES, normalize_embeddings=True, show_progress_bar=False)
                        else:
                            raise e_mem

                    similarities = cosine_similarity(query_embeddings, chunk_embeddings)
                    retrieval_time = time.time() - start_retrieval
                    
                    max_sims = np.max(similarities, axis=1)
                    avg_sim = np.mean(max_sims)
                    cosine_scores = [f"{score:.4f}" for score in max_sims]
                    
                    # Get sample result from the first query
                    top_idx_0 = np.argmax(similarities[0])
                    sample_result = chunks_text[top_idx_0].replace("\n", " ").strip()[:200]
                    
                    embedding_dim = model.get_sentence_embedding_dimension()
                    curr_device = next(model.parameters()).device
                    
                    output = f"""
============================================================
Chunker: {strategy}
Chunk Size: {size}
Embedding: {model_name}
Chunks: {num_chunks}
Avg Chunk Length: {avg_len:.1f}
Dim: {embedding_dim}
Device: {curr_device}
Build Time: {build_time:.2f}s
Retrieval Time: {retrieval_time:.4f}s
Avg Cosine Similarity: {avg_sim:.4f} (higher is better)
All Cosine Scores: {cosine_scores}
Sample Result: "{sample_result}..."
============================================================
"""
                    print(output, flush=True)
                    with open(results_file, "a", encoding='utf-8') as f:
                        f.write(output + "\n")
                        
                except Exception as e:
                    print(f"    Error evaluating model {model_name}: {e}", flush=True)
                finally:
                    # 3. Explicitly Unload Model
                    print(f"    Unloading {model_name}...", flush=True)
                    del model
                    clear_memory()

    print(f"\nBenchmark Complete. Results saved to {results_file}")

if __name__ == "__main__":
    run_benchmark()
