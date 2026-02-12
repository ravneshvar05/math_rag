
import sys
from app.pipeline import MathRAGPipeline
from utils.logging import get_logger

# Force UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def check_index_content():
    print("--- Inspecting Index Content for Exercise 3.1 ---")
    pipeline = MathRAGPipeline()
    pipeline._init_query_components()
    
    # Query
    results = pipeline.retrieval_pipeline.search("Exercise 3.1", top_k=3)
    
    for r in results:
        if "EXERCISE 3.1" in r.chunk.text_content:
            print(f"\n[Rank {r.rank}] Score: {r.score}")
            print(f"FULL Chunk Content:\n{r.chunk.text_content}")
            print("-" * 20)

if __name__ == "__main__":
    check_index_content()
