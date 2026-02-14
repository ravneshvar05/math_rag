import sys
from pathlib import Path
import json
import logging

# Add project root to path
sys.path.append(str(Path.cwd()))

from app.pipeline import MathRAGPipeline
from utils.logging import get_logger

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = get_logger(__name__)

def debug_query():
    pipeline = MathRAGPipeline()
    
    query = "give me excercise 3.3 questions only"
    
    print(f"\n--- Debugging Query: '{query}' ---")
    
    # 1. Inspect Retrieval Results directly
    # We need to access the retrieval pipeline inside the main pipeline
    pipeline._init_query_components()
    
    results = pipeline.retrieval_pipeline.search(query, top_k=5)
    
    print(f"\nFound {len(results)} chunks:")
    
    for i, res in enumerate(results):
        chunk = res.chunk
        print(f"\n[Rank {i+1}] Score: {res.score:.4f}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Location: Class {chunk.class_level} | Ch {chunk.chapter_number} | {chunk.section_name}")
        print(f"Content Type: {chunk.content_type.value}")
        print(f"Text Preview: {chunk.text_content[:200]}...")
        
        if chunk.images:
            print(f"Linked Images ({len(chunk.images)}):")
            for img in chunk.images:
                print(f"  - ID: {img.image_id}")
                print(f"  - Path: {img.image_path}")
                print(f"  - Desc: {img.description}")
        else:
            print("No Linked Images")

if __name__ == "__main__":
    debug_query()
