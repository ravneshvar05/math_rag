import sys
import os
from unittest.mock import MagicMock
from typing import Dict, Any, List

sys.path.append(os.getcwd())

from chunking.structure_aware_chunker import StructureAwareChunker
from utils.schema import ContentType

def test_smart_chunking():
    print("Testing Smart Chunking Logic...")
    
    # Mock config
    config = {
        'max_tokens': 100, # Small limit to force splitting
        'min_tokens': 10,
        'overlap_tokens': 0
    }
    
    chunker = StructureAwareChunker(config)
    
    # create a large text (approx 400 tokens / 1600 chars)
    # Paragraphs separated by \n\n
    para1 = "This is paragraph 1. " * 20
    para2 = "This is paragraph 2. " * 20
    para3 = "This is paragraph 3. " * 20
    para4 = "This is paragraph 4. " * 20
    
    large_text = f"{para1}\n\n{para2}\n\n{para3}\n\n{para4}"
    
    buffer = {
        'text': large_text,
        'type': 'exercise',
        'number': '3.2',
        'start_page': 1
    }
    
    # Mock context
    doc_id = "test_doc"
    class_level = "11"
    chapter = {'number': 3, 'name': 'Trig'}
    section = {'name': 'Exercises'}
    
    # Mock images
    images = [{'image_id': 'fig_1', 'image_path': 'path/to/img', 'page_number': 1}]
    
    # Run _create_collection_chunk
    chunks = chunker._create_collection_chunk(
        buffer,
        doc_id,
        class_level,
        chapter,
        section,
        page_images=images
    )
    
    print(f"\nInput Text Length: {len(large_text)} chars")
    print(f"Max Chars Limit: {chunker.max_tokens * 3.5}")
    print(f"Generated Chunks: {len(chunks)}")
    
    # Verifications
    failures = []
    
    if len(chunks) <= 1:
        failures.append("FAIL: Did not split large text.")
    else:
        print(f"PASS: Split into {len(chunks)} chunks.")
        
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1} Length: {len(chunk.text_content)}")
        
        # Check metadata
        if chunk.exercise_number != '3.2':
            failures.append(f"FAIL: Chunk {i+1} missing exercise number.")
        
        # Check image linking
        if not chunk.images:
            failures.append(f"FAIL: Chunk {i+1} missing linked images.")
            
        # Check header
        if i > 0:
            if not chunk.text_content.startswith("[Exercise 3.2 (Part"):
                 failures.append(f"FAIL: Chunk {i+1} missing continuation header.")
    
    if not failures:
        print("\nALL TESTS PASSED for Smart Chunking.")
    else:
        print("\nFAILURES:")
        for f in failures:
            print(f)

if __name__ == "__main__":
    test_smart_chunking()
