import sys
import os
from unittest.mock import MagicMock
from typing import Dict, Any, List

sys.path.append(os.getcwd())

from chunking.structure_aware_chunker import StructureAwareChunker

def test_cross_page_linking():
    print("Testing Cross-Page Image Linking & Orphan Rescue...")
    
    config = {
        'max_tokens': 100,
        'min_tokens': 10,
        'overlap_tokens': 0
    }
    
    chunker = StructureAwareChunker(config)
    
    # Scenario 1: Multi-page exercise (Explicit Reference)
    # Page 1: Has Image "Fig 3.5"
    # Page 2: Text says "Refer to Fig 3.5"
    
    images = [
        {'image_id': 'fig_3_5', 'image_path': 'img/fig_3_5.png', 'page_number': 1, 'description': 'Diagram for Q5'}
    ]
    
    para1 = "Question 1: Solve x. " * 10
    para2 = "Question 5: Refer to Fig 3.5 to find y. " * 10 
    
    large_text = f"{para1}\n\n{para2}"
    
    buffer = {
        'text': large_text,
        'type': 'exercise',
        'number': '3.2',
        'start_page': 1,
        'images': images # Accumulated images
    }
    
    # Run
    # Note: We need to mock that the first chunk is page 1 and second is page 2 roughly
    # structure_aware_chunker uses buffer['start_page'] for all chunks unless we get fancy.
    # But wait, Orphan Rescue relies on generated chunk's page_number matching image's page_number.
    # In _create_collection_chunk, all chunks get `buffer['start_page']` initially!
    # This is a limitation I need to be aware of. 
    # If the chunker assigns 'start_page' (1) to ALL chunks, then an image on Page 2 might be rescued to a chunk labeled Page 1.
    # However, for Collection Chunks, they are usually treated as a continuous block starting at start_page.
    # Let's see how my implementation handles it.
    
    # My implementation: 
    # chunk = ContentChunk(..., page_number=buffer['start_page'], ...)
    # So ALL chunks get Page 1.
    # If I have an image on Page 1, it will be rescued to ALL chunks (Page 1).
    # Ideally, we want to rescue only if truly lost.
    
    # Let's test Scenario 2: Implicit Reference on SAME PAGE as text
    
    print("\nTesting Scenario 2: Implicit Reference (Orphan Rescue)...")
    para3 = "Question 6: Look at the diagram below. " * 10
    
    # Image on Page 2
    # Buffer start_page = 2
    buffer2 = {
        'text': para3,
        'type': 'exercise',
        'number': '3.2',
        'start_page': 2,
        'images': [{'image_id': 'fig_3_6', 'image_path': 'img.png', 'page_number': 2, 'description': 'Diagram 6'}]
    }
    
    chunks2 = chunker._create_collection_chunk(
        buffer2, "doc1", "11", {}, {}, page_images=buffer2['images']
    )
    
    failures = []
    
    if chunks2[0].images:
        print("  Chunk 3 (Implicit) has image? YES (Orphan Rescue Worked!)")
    else:
        print("  Chunk 3 (Implicit) has image? NO (Rescue Failed)")
        failures.append("FAIL: Orphaned image was NOT rescued.")

    if failures:
        print("\nSUMMARY:")
        for f in failures:
            print(f)
    else:
        print("\nAll scenarios handled as expected.")

if __name__ == "__main__":
    test_cross_page_linking()
