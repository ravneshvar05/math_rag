
import sys
import os
import fitz  # PyMuPDF

# Force UTF-8 output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def check_for_exercise_3_1(pdf_path):
    print(f"Checking: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
        found = False
        for i, page in enumerate(doc):
            text = page.get_text()
            if "Exercise 3.1" in text or "EXERCISE 3.1" in text:
                print(f"FOUND 'Exercise 3.1' on Page {i+1}")
                print("-" * 20)
                print(text[:500]) # Preview
                found = True
                break
        
        if not found:
            print("Did NOT find 'Exercise 3.1' in this file.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    target_file = "Mathematics-11 1-43-75.pdf"
    full_path = os.path.join("data", "raw", target_file)
    
    if os.path.exists(full_path):
        check_for_exercise_3_1(full_path)
    else:
        print(f"File {target_file} not found locally.")
