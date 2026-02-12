
import sys
import os
from pathlib import Path
from chunking.structure_aware_chunker import StructureAwareChunker
from extraction.pdf_extractor import PDFExtractor
from extraction.content_parser import ContentParser
from config import get_yaml_config

# Force UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def evaluate_chunking(pdf_name):
    print(f"Evaluating Chunking for: {pdf_name}")
    pdf_path = Path("data/raw") / pdf_name
    
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        return

    # 1. Extract (Mocking pipeline steps)
    extractor = PDFExtractor(str(pdf_path), "data/processed")
    extraction_result = extractor.extract_all()
    
    # 2. Parse Content
    parser = ContentParser(get_yaml_config('pdf_processing'))
    # structured_content = parser.parse_document_structure(extraction_result['pages']) # Not strictly needed for chunker logic test
    
    # 3. Chunk
    chunker = StructureAwareChunker(get_yaml_config('chunking'))
    # chunk_document(self, pages: List[Dict], document_id: str, class_level: str)
    chunks = chunker.chunk_document(extraction_result['pages'], "eval_doc", "11")
    
    print(f"\nTotal Chunks: {len(chunks)}")
    
    # 4. Analyze Boundaries
    print("\n--- Chunk Boundary Analysis ---")
    
    prev_end = ""
    for i, chunk in enumerate(chunks[:20]): # Check first 20 chunks
        content = chunk.text_content.strip()
        print(f"\nChunk {i} [Type: {chunk.content_type.value}]")
        print(f"Start: {content[:50].replace(chr(10), ' ')}...")
        print(f"End:   ...{content[-50:].replace(chr(10), ' ')}")
        
        # Check if it cut off a sentence?
        if not content.endswith(('.', ':', '?', '!')):
             print(">> WARNING: Chunk might have cut off mid-sentence.")
             
        # Check if it captured a header?
        if "Example" in content[:20] or "Exercise" in content[:20]:
            print(">> INFO: captured logical header.")
            
    # Check specifically for "Exercise 3.1" if relevant file
    print("\n--- Searching for 'Exercise 3.1' in Chunks ---")
    found = False
    for chunk in chunks:
        if "Exercise 3.1" in chunk.text_content or "EXERCISE 3.1" in chunk.text_content:
            print(f"FOUND in Chunk {chunk.chunk_id} [Type: {chunk.content_type.value}]")
            print(f"--- CONTENT PREVIEW ---\n{chunk.text_content[:500]}\n-----------------------")
            found = True
            break
    if not found:
        print("Exercise 3.1 NOT found in any chunk.")

if __name__ == "__main__":
    # Test on Chapter 3 file if available, else the chapter 9 file
    files = os.listdir("data/raw")
    target = "Mathematics-11 1-43-75.pdf" if "Mathematics-11 1-43-75.pdf" in files else "Mathematics-11 1-151-175.pdf"
    evaluate_chunking(target)
