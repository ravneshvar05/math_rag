import sys
import os
import re
from unittest.mock import MagicMock
from typing import Dict, Any, List

sys.path.append(os.getcwd())

from chunking.structure_aware_chunker import StructureAwareChunker
from utils.schema import ContentType

def test_page_segmentation():
    print("Testing Concept-Aware Page Segmentation...")
    
    config = {
        'max_tokens': 800,
        'min_tokens': 100,
        'overlap_tokens': 50
    }
    chunker = StructureAwareChunker(config)
    
    # Simulate Page Text
    # 1. Tail of Ex 3.3
    # 2. Section Header
    # 3. Theorem
    # 4. Example 18
    # 5. Start of Ex 3.4
    
    page_text = """
    (Question 10 continued) ... find the value of x.
    
    3.4 TRIGONOMETRIC EQUATIONS
    
    Theorem 1 The general solution to sin x = 0 is x = n \u03c0.
    Proof: We know that...
    
    Example 18 Find the principal solution of the equation sin x = 3/2.
    Solution: We know that sin pi/3 = ...
    
    EXERCISE 3.4
    1. Find the principal solution of tan x = 1.
    """
    
    # Initial State: Collecting Ex 3.3
    chunker.collecting_exercise = True # Mocking internal state if possible? 
    # Actually, the method is chunk_document, which holds the state. 
    # I need to mock the entire process or trust the logic.
    # Let's run `chunk_document` with a setup that puts it in "collecting" state.
    
    # To test "Header breaks collection", I need the previous page to start Ex 3.3.
    
    page1 = {
        'page_number': 1,
        'text': "EXERCISE 3.3\n1. Solve this.",
        'images': []
    }
    
    page2 = {
        'page_number': 2,
        'text': page_text,
        'images': []
    }
    
    doc_id = "test_doc"
    class_level = "11"
    
    chunks = chunker.chunk_document([page1, page2], doc_id, class_level)
    
    print(f"\nTotal Chunks Created: {len(chunks)}")
    
    print(f"{'Type':<15} | {'Num':<15} | {'Preview'}")
    print("-" * 60)
    
    for c in chunks:
        num = c.exercise_number or c.example_number or "-"
        preview = c.text_content.replace('\n', ' ')[:40]
        print(f"{c.content_type.value:<15} | {num:<15} | {preview}")

    # Verifications
    
    # 1. Exercise 3.3 should contain "Solve this" AND "Question 10 continued"
    ex33 = next((c for c in chunks if c.content_type.value == 'exercise' and c.exercise_number == '3.3'), None)
    if ex33:
        if "Question 10 continued" in ex33.text_content:
            print("PASS: Ex 3.3 captured tail text correctly.")
        else:
            print("FAIL: Ex 3.3 missed tail text.")
    else:
        print("FAIL: Ex 3.3 chunk missing.")
        
    # 2. Theorem should be a TEXT chunk (not part of Ex 3.3 or Ex 3.4)
    # Check for text chunk containing "Theorem 1"
    theorem = next((c for c in chunks if "Theorem 1" in c.text_content and c.content_type.value not in ['exercise', 'example']), None)
    # Note: My logic creates 'text' chunks for independent segments.
    # Wait, my logic calls `_chunk_page` which might detect content type as 'theorem' if math_detector does its job.
    # StructureAwareChunker uses `_create_simple_chunk` which uses `math_detector.detect_content_type`.
    # `math_detector` maps 'Theorem' -> ContentType.THEOREM.
    
    if theorem:
        print(f"PASS: Theorem 1 detected as independent chunk ({theorem.content_type.value}).")
    else:
        # It might have been classified as TEXT if detector is weak, but it shouldn't be EXERCISE.
        # Let's check if any chunk has "Theorem 1"
        c_theo = next((c for c in chunks if "Theorem 1" in c.text_content), None)
        if c_theo:
            print(f"WARN: Theorem 1 found in {c_theo.content_type.value} {c_theo.exercise_number or c_theo.example_number}. Should be independent.")
        else:
            print("FAIL: Theorem 1 text missing.")

    # 3. Example 18 should be EXAMPLE chunk
    ex18 = next((c for c in chunks if c.content_type.value == 'example' and c.example_number == '18'), None)
    if ex18:
        print("PASS: Example 18 chunk created.")
        if "Find the principal" in ex18.text_content:
             print("PASS: Example 18 has correct content.")
    else:
        print("FAIL: Example 18 chunk missing.")
        
    # 4. Ex 3.4 should be started
    ex34 = next((c for c in chunks if c.content_type.value == 'exercise' and c.exercise_number == '3.4'), None)
    if ex34:
        print("PASS: Exercise 3.4 chunk created.")
    else:
        print("FAIL: Exercise 3.4 chunk missing.")

if __name__ == "__main__":
    test_page_segmentation()
