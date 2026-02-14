import sys
sys.stdout.reconfigure(encoding='utf-8')
import fitz
import re

def debug_specific_diagram():
    pdf_path = "data/raw/math_class_11.pdf"
    doc = fitz.open(pdf_path)
    page_num = 10 # Page 11 is index 10
    page = doc[page_num]
    
    print(f"--- Page {page_num+1} Metrics ---")
    print(f"Page Rect: {page.rect}")
    print(f"Page Width: {page.rect.width}, Height: {page.rect.height}")
    
    # 1. Find the caption "Fig 1.1"
    blocks = page.get_text("blocks")
    caption_block = None
    for b in blocks:
        if "Fig" in b[4] and "1.1" in b[4]:
            caption_block = b
            print(f"Found Caption: '{b[4].strip()}'")
            print(f"Caption Rect: {b[:4]}")
            break
            
    if not caption_block:
        print("Caption 'Fig 1.1' not found!")
        return

    # 2. Simulate Extraction Logic
    caption_rect = fitz.Rect(caption_block[:4])
    split_x = 0 # Assuming single column for now, but let's check
    
    # Check column detection logic
    # (Simplified version of _detect_columns for debug)
    # ... assuming 0 for now as it looks like a standard page
    
    col_min_x = 0
    col_max_x = page.rect.width
    
    # Vertical search area
    search_area = fitz.Rect(col_min_x, max(0, caption_rect.y0 - 300), col_max_x, caption_rect.y0)
    print(f"Search Area: {search_area}")
    
    # 3. Analyze Drawings
    all_drawings = page.get_drawings()
    print(f"Total Drawings on Page: {len(all_drawings)}")
    
    candidates = []
    
    for i, d in enumerate(all_drawings):
        d_rect = d["rect"]
        
        # Check intersection
        intersects = d_rect.intersects(search_area)
        
        # Check containment (STRICT)
        contained = (d_rect.x0 >= col_min_x and d_rect.x1 <= col_max_x)
        
        # Check background heuristic
        is_background = (d_rect.width > page.rect.width * 0.9 or d_rect.height > page.rect.height * 0.5)
        
        # Log purely relevant ones or large ones
        if intersects or is_background:
            status = "REJECTED"
            if intersects and contained and not is_background:
                status = "ACCEPTED"
                candidates.append(d_rect)
            
            print(f"Drawing {i}: {d_rect}")
            print(f"  Dims: {d_rect.width:.1f}x{d_rect.height:.1f}")
            print(f"  Intersects Search: {intersects}")
            print(f"  Contained in Col: {contained}")
            print(f"  Is Background (>90%): {is_background}")
            print(f"  -> {status}")

    # 4. Resulting Union BBox
    if candidates:
        union_box = candidates[0]
        for c in candidates[1:]:
            union_box |= c
        print(f"--- FINAL SELECTED BBOX ---")
        print(f"{union_box}")
        print(f"Width: {union_box.width}, Height: {union_box.height}")
    else:
        print("No drawings selected!")

if __name__ == "__main__":
    debug_specific_diagram()
