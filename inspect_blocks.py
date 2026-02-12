
import sys
import fitz  # PyMuPDF

# Force UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def inspect_blocks(pdf_path):
    print(f"Inspecting blocks in: {pdf_path}")
    doc = fitz.open(pdf_path)
    
    for i, page in enumerate(doc):
        text = page.get_text()
        if "EXERCISE 3.1" in text:
            print(f"\n--- Found 'EXERCISE 3.1' on Page {i+1} ---")
            blocks = page.get_text("blocks")
            for b in blocks:
                block_text = b[4]
                if "EXERCISE 3.1" in block_text:
                    print(f"BLOCK CONTENT FOUND:")
                    print(block_text.encode('utf-8', errors='replace'))
                    print("-" * 20)
            return

if __name__ == "__main__":
    inspect_blocks("data/raw/Mathematics-11 1-43-75.pdf")
