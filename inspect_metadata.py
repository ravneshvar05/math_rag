import json
import os

def inspect_metadata():
    metadata_path = "data/metadata.json"
    if not os.path.exists(metadata_path):
        print(f"Error: {metadata_path} not found.")
        return

    print(f"Loading metadata from {metadata_path}...")
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} chunks.")
    
    spike_candidates = []
    
    for chunk_id, chunk in data.items():
        text = chunk.get('text_content', '')
        # Check for Exercise 3.2
        if "Exercise 3.2" in text or "EXERCISE 3.2" in text:
            spike_candidates.append({
                'id': chunk_id,
                'len': len(text),
                'type': chunk.get('content_type'),
                'chapter': chunk.get('chapter_number'),
                'preview': text[:100]
            })

    print(f"\nFound {len(spike_candidates)} chunks related to 'Exercise 3.2':")
    
    total_len = 0
    for c in spike_candidates:
        print(f"\nID: {c['id']}")
        print(f"Type: {c['type']}")
        print(f"Length: {c['len']} chars")
        print(f"Preview: {c['preview']}...")
        total_len += c['len']

    print(f"\nTotal Context Length from these chunks: {total_len} chars")
    print(f"Est. Tokens (chars / 4): {total_len / 4}")

if __name__ == "__main__":
    inspect_metadata()
