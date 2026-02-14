"""Debug script to check how Example 13 is being extracted."""

import fitz  # PyMuPDF
from pathlib import Path

# Find the PDF
pdf_dir = Path("data/raw")
pdf_files = list(pdf_dir.glob("*.pdf"))

print("Available PDFs:")
for i, pdf in enumerate(pdf_files, 1):
    print(f"  {i}. {pdf.name}")

# Use the trigonometry PDF (should contain Example 13)
trig_pdf = [p for p in pdf_files if "43-75" in p.name]

if not trig_pdf:
    print("\nNo trigonometry PDF found!")
    exit(1)

pdf_path = trig_pdf[0]
print(f"\nUsing: {pdf_path.name}\n")

# Open PDF
doc = fitz.open(str(pdf_path))

# Search for "Example 13" across all pages
found_pages = []
for page_num, page in enumerate(doc):
    text = page.get_text()
    if "Example 13" in text or "EXAMPLE 13" in text:
        found_pages.append((page_num + 1, page))

print(f"Found 'Example 13' on {len(found_pages)} page(s)\n")

for page_num, page in found_pages:
    output = []
    output.append("="*80)
    output.append(f"PAGE {page_num}")
    output.append("="*80)
    output.append("")
    
    # Get text in different formats to compare
    
    # 1. Simple text extraction
    output.append("--- SIMPLE TEXT EXTRACTION ---")
    simple_text = page.get_text()
    
    # Find Example 13 section
    start_idx = simple_text.find("Example 13")
    if start_idx == -1:
        start_idx = simple_text.find("EXAMPLE 13")
    
    # Extract ~800 characters after "Example 13"
    example_text = simple_text[start_idx:start_idx + 800] if start_idx != -1 else simple_text[:800]
    output.append(example_text)
    output.append("")
    
    # 2. Block-level extraction (what your system uses)
    output.append("--- BLOCK-LEVEL EXTRACTION (Current System) ---")
    blocks = page.get_text("blocks")
    
    example_found = False
    for block_idx, block in enumerate(blocks):
        if block[6] != 0:  # Skip non-text
            continue
        
        block_text = block[4]
        
        if "Example 13" in block_text or "EXAMPLE 13" in block_text:
            example_found = True
            
        if example_found:
            output.append(f"Block {block_idx}: {block_text}")
            output.append("")
            
            # Print next 5 blocks after Example 13
            if block_idx <= len(blocks) - 6:
                for i in range(1, 6):
                    next_block = blocks[block_idx + i]
                    if next_block[6] == 0:
                        output.append(f"Block {block_idx + i}: {next_block[4]}")
                        output.append("")
            break
    
    # Write to file with UTF-8 encoding
    with open("d:/ProjMath/math_rag/example13_extraction.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

doc.close()

print(f"\n{'='*80}")
print("Output saved to: example13_extraction.txt")
print(f"{'='*80}")
