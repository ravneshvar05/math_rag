import sys
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path.cwd()))

from storage.metadata_store import MetadataStore

def debug_metadata():
    print("--- Inspecting Metadata for Exercise 3.3 Chunks ---")
    
    # Load metadata store directly
    store = MetadataStore()
    
    # Filter for chunks that look like Exercise 3.3
    # Use loose matching since we don't know exact chunk IDs
    
    relevant_chunks = []
    
    for chunk_id, data in store.data.items():
        text = data.get('text_content', '').lower()
        section = data.get('section_name', '').lower()
        
        if 'exercise 3.3' in text or '3.3' in section:
            relevant_chunks.append(data)
            
    print(f"Found {len(relevant_chunks)} potentially relevant chunks.")
    
    for chunk in relevant_chunks[:5]:
        print(f"\nChunk ID: {chunk.get('chunk_id')}")
        print(f"Section: {chunk.get('section_name')}")
        print(f"Text Preview: {chunk.get('text_content')[:100]}...")
        
        images = chunk.get('images', [])
        if images:
            print(f"Linked Images ({len(images)}):")
            for img in images:
                print(f"  - {img.get('image_id')}: {img.get('description')}")
        else:
            print("No Linked Images")

if __name__ == "__main__":
    debug_metadata()
