"""Test the improved OCR extraction on Example 13"""

from extraction.pdf_extractor import PDFExtractor

def test_example_13():
    print("Testing OCR-Enhanced Extraction on Example 13...")
    
    extractor = PDFExtractor('data/raw/Mathematics-11 1-43-75.pdf', 'data/processed')
    result = extractor.extract_all()
    
    # Page 23 contains Example 13 (index 22)
    page_23 = result['pages'][22]
    
    print(f"\n=== Page 23 Extraction ===")
    print(f"Total blocks: {len(page_23['blocks'])}")
    
    # Find Example 13
    example_13_blocks = []
    for i, block in enumerate(page_23['blocks']):
        if 'example 13' in block['text'].lower():
            example_13_blocks.append((i, block))
            print(f"\n[Block {i}] Type: {block['type']}")
            print(f"Text: {block['text'][:300]}...")
    
    if not example_13_blocks:
        print("\nExample 13 not found on page 23")
        return
    
    # Check the formula quality
    print("\n\n=== Formula Quality Check ===")
    for idx, block in example_13_blocks:
        text = block['text']
        
        # Check if fractions are preserved
        has_division = '/' in text or 'divided' in text.lower()
        has_fraction_words = 'numerator' in text.lower() or 'denominator' in text.lower()
        
        print(f"Block {idx}:")
        print(f"  - Contains '/' : {has_division}")
        print(f"  - Fraction terminology: {has_fraction_words}")
        print(f"  - sin(x+y) present: {'sin(x+y)' in text or 'sin (x + y)' in text}")
        print(f"  - sin(x-y) present: {'sin(x-y)' in text or 'sin (x - y)' in text or 'sin(x—y)' in text}")
        
    # Show full page text
    print("\n=== Full Page Text (first 1000 chars) ===")
    print(page_23['text'][:1000])

if __name__ == "__main__":
    test_example_13()
