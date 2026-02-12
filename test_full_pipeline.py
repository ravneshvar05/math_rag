
import sys
import os
from pathlib import Path
from app.pipeline import MathRAGPipeline
from utils.logging import get_logger

# Force UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

logger = get_logger(__name__)

def test_pipeline():
    print("--- Starting Full Pipeline Test ---")
    
    # 1. Initialize
    pipeline = MathRAGPipeline()
    
    # 2. Index Chapter 3 (Trigonometric Functions)
    pdf_path = "data/raw/Mathematics-11 1-43-75.pdf"
    if not os.path.exists(pdf_path):
        print(f"ERROR: File {pdf_path} not found.")
        return

    print(f"\n[Indexing] Processing {pdf_path}...")
    pipeline.index_document(
        pdf_path=pdf_path,
        class_level="11",
        force_reindex=True
    )
    
    # 3. Test Retrieval - Exercise 3.1 (Entity Query)
    query_1 = "what are the questions in Exercise 3.1"
    print(f"\n[Query 1] '{query_1}'")
    
    # Initialize query components to ensure retrieval_pipeline is ready
    pipeline._init_query_components()
    
    # We use the internal retrieval pipeline directly to inspect results before LLM
    # pipeline.retrieval_pipeline.search(query)
    
    results_1 = pipeline.retrieval_pipeline.search(query_1, top_k=3)
    
    found_ex = False
    for r in results_1:
        print(f"  - Rank {r.rank} (Score {r.score:.4f}): {r.chunk.text_content[:100].replace(chr(10), ' ')}...")
        if "EXERCISE 3.1" in r.chunk.text_content:
            found_ex = True
            
    if found_ex:
        print("  >> SUCCESS: Found 'EXERCISE 3.1' chunk.")
    else:
        print("  >> FAILURE: Did not find 'EXERCISE 3.1' chunk.")

    # 4. Test Retrieval - Example (Entity Query)
    # Let's pick an example we know exists in Chapter 3.
    # From previous checks, Example 1 might be there? Or let's search specifically for "Example 6" (often in 3.2)
    # Actually, let's just use "Example 1" as that was the original complaint.
    query_2 = "Example 1"
    print(f"\n[Query 2] '{query_2}'")
    
    results_2 = pipeline.retrieval_pipeline.search(query_2, top_k=3)
    
    found_example = False
    for r in results_2:
        print(f"  - Rank {r.rank} (Score {r.score:.4f}): {r.chunk.text_content[:100].replace(chr(10), ' ')}...")
        if "Example 1" in r.chunk.text_content:
             found_example = True
             
    if found_example:
        print("  >> SUCCESS: Found 'Example 1'.")
    else:
        print("  >> FAILURE: Did not find 'Example 1'.")

if __name__ == "__main__":
    try:
        test_pipeline()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
