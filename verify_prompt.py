import sys
import os
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.getcwd(), '.'))

from llm.groq_client import GroqClient

def verify_optimization():
    print("Verifying prompt optimization...")
    
    # Mock chunk data
    chunk_with_extras = {
        'class_level': '11',
        'chapter_number': 1,
        'chapter_name': 'Sets',
        'section_name': 'Introduction',
        'content_type': 'text',
        'text_content': 'The set of natural numbers is N = {1, 2, 3, ...}. Equation: $x^2 = 4$.',
        'equations': ['$x^2 = 4$'],  # Redundant
        'images': [
            {
                'description': 'A Venn diagram showing set A subset of B',
                'path': 'd:/ProjMath/math_rag/img/venn_diagram.png' # Path should be hidden
            }
        ],
        'tables': []
    }
    
    # Initialize client (mock API key to avoid error during init if checks present, 
    # though GroqClient init doesn't validate key immediately usually)
    client = GroqClient(api_key="mock_key")
    
    # Mock the actual generate call to capture prompt without hitting API
    client.generate = MagicMock(return_value={"content": "Mock Response"})
    
    # Call generate_with_context
    client.generate_with_context("What is a set?", [chunk_with_extras])
    
    # Inspect arguments passed to generate
    call_args = client.generate.call_args
    if not call_args:
        print("Error: client.generate was not called.")
        return
        
    prompt = call_args.kwargs.get('prompt')
    if not prompt:
        prompt = call_args.args[0] if call_args.args else "No prompt found"
        
    print("\nGenerated Prompt Context:\n" + "="*40)
    print(prompt)
    print("="*40 + "\n")
    
    # Verification Checks
    failures = []
    
    # 1. Check for Equation list
    if "Equations:" in prompt and "$x^2 = 4$" in prompt.split("Equations:")[1]:
        failures.append("FAIL: Redundant equation list found.")
    else:
        print("PASS: Redundant equation list removed.")
        
    # 2. Check for File Path
    if "d:/ProjMath/math_rag/img/venn_diagram.png" in prompt:
         failures.append("FAIL: File path found in prompt.")
    else:
        print("PASS: File path removed.")

    # 3. Check for Description
    if "A Venn diagram showing set A subset of B" not in prompt:
        failures.append("FAIL: Image description missing.")
    else:
        print("PASS: Image description preserved.")

    if failures:
        print("\nVerification FAILED:")
        for f in failures:
            print(f)
    else:
        print("\nVerification SUCCESS: Prompt optimized.")

if __name__ == "__main__":
    verify_optimization()
