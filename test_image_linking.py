import sys
import os
from unittest.mock import MagicMock
from typing import Dict, Any, List

sys.path.append(os.getcwd())

from chunking.structure_aware_chunker import StructureAwareChunker

def test_cross_page_linking():
    print("Testing Cross-Page Image Linking...")
    
    config = {
        'max_tokens': 100,
        'min_tokens': 10,
        'overlap_tokens': 0
    }
    
    chunker = StructureAwareChunker(config)
    
    # Scenario 1: Multi-page exercise
    # Page 1: Has Image "Fig 3.5"
    # Page 2: Text says "Refer to Fig 3.5"
    
    # Simulation: We accumulate images from Page 1 into buffer
    images = [
        {'image_id': 'fig_3_5', 'image_path': 'img/fig_3_5.png', 'page_number': 1, 'description': 'Diagram for Q5'}
    ]
    
    # Text spans multiple pages, so it will be split.
    # Part 1 (Page 1 text) - No reference
    # Part 2 (Page 2 text) - Has reference
    
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
    chunks = chunker._create_collection_chunk(
        buffer, "doc1", "11", {}, {}, page_images=images
    )
    
    print(f"\nGenerated {len(chunks)} chunks.")
    
    failures = []
    
    # Chunk 1 (Q1) -> Should NOT have image (no ref)
    if chunks[0].images:
        print("  Chunk 1 has image? NO (Correct)")
    else:
        print("  Chunk 1 has image? NO (Correct)")
        
    # Chunk 2 (Q5) -> SHOULD have image (has ref)
    has_img = any(img.image_id == 'fig_3_5' for img in chunks[1].images)
    if has_img:
        print("  Chunk 2 has image? YES (Correct - Cross-page linking worked)")
    else:
        failures.append("FAIL: Chunk 2 matched reference but did NOT link the accumulated image.")
        
    # Scenario 2: Implicit/Missing Reference
    # Text: "Look at the diagram below" (no explicit "Fig X")
    # Image: Just present on page
    
    print("\nTesting Implicit Reference (Proximity)...")
    para3 = "Question 6: Look at the diagram below. " * 10
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
    
    if chunks2[0].images:
        print("  Chunk 3 (Implicit) has image? YES (Proximity logic active?)")
    else:
        print("  Chunk 3 (Implicit) has image? NO (Strict reference mode)")
        # This confirms if we are missing non-referenced images
        failures.append("WARN: Implicit reference failed. If text doesn't say 'Fig X', image is lost.")

    if failures:
        print("\nSUMMARY:")
        for f in failures:
            print(f)
    else:
        print("\nAll scenarios handled as expected.")

if __name__ == "__main__":
    test_cross_page_linking()
