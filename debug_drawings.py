import fitz
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_page_drawings(pdf_path, page_num):
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    
    print(f"Page {page_num} size: {page.rect}")
    
    drawings = page.get_drawings()
    print(f"Found {len(drawings)} drawings")
    
    for i, d in enumerate(drawings):
        rect = d["rect"]
    for i, d in enumerate(drawings):
        rect = d["rect"]
        fill = d.get("fill")
        color = d.get("color")
        # Check if it's large
        if rect.width > page.rect.width * 0.8 and rect.height > page.rect.height * 0.8:
             print(f"HUGE Drawing {i}: {rect} Fill: {fill} Color: {color}")

if __name__ == "__main__":
    pdf_path = "data/raw/math_class_11.pdf"
    debug_page_drawings(pdf_path, 10) # Page 10 (0-indexed) is page 11 (1-indexed) in extraction
