
import sys
import os
import fitz  # PyMuPDF

# Force UTF-8 output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_pdf_structure(pdf_path):
    print(f"Analyzing: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        print(f"Total Pages: {len(doc)}")
        
        # Analyze first few pages where examples likely appear
        for i, page in enumerate(doc):
            if i > 5: break # Just check first 5 pages for patterns
            
            print(f"\n--- Page {i+1} ---")
            text = page.get_text()
            print(text[:1000]) # Print first 1000 chars to see layout
            
            # Look for "Example" keywords specifically
            print("\n[Targeted Search for 'Example']")
            lines = text.split('\n')
            for line in lines:
                if 'example' in line.lower():
                    print(f"FOUND: '{line.strip()}'")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check for the specific file the user mentioned, or list available
    target_file = "Mathematics-11 1-151-175.pdf"
    full_path = os.path.join("data", "raw", target_file)
    
    if os.path.exists(full_path):
        analyze_pdf_structure(full_path)
    else:
        print(f"File {target_file} not found. Checking directory...")
        for f in os.listdir(os.path.join("data", "raw")):
            if f.endswith(".pdf"):
                print(f"Found: {f}")
                analyze_pdf_structure(os.path.join("data", "raw", f))
                break
