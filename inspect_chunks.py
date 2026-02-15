import json
import os

def inspect_chunks():
    metadata_path = "data/metadata.json"
    if not os.path.exists(metadata_path):
        print(f"Error: {metadata_path} not found.")
        return

    print(f"Loading metadata from {metadata_path}...")
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Writing report to chunks_report.txt...")
    with open("chunks_report.txt", "w", encoding="utf-8") as f:
        f.write(f"Total Chunks: {len(data)}\n")
        f.write(f"{'ID':<38} | {'Type':<10} | {'Number':<8} | {'Page':<4} | {'Len':<6} | {'Preview'}\n")
        f.write("-" * 120 + "\n")
        
        sorted_chunks = sorted(data.values(), key=lambda x: (x.get('page_number', 0), x.get('chunk_id')))
        
        for chunk in sorted_chunks:
            c_id = chunk.get('chunk_id')
            c_type = chunk.get('content_type')
            
            # Get number
            if c_type == 'exercise':
                num = chunk.get('exercise_number')
            elif c_type == 'example':
                num = chunk.get('example_number')
            else:
                num = "-"
                
            page = chunk.get('page_number', 0)
            length = len(chunk.get('text_content', ''))
            preview = chunk.get('text_content', '').replace('\n', ' ')[:50]
            
            f.write(f"{c_id:<38} | {c_type:<10} | {str(num):<8} | {str(page):<4} | {str(length):<6} | {preview}\n")
    print("Done.")

if __name__ == "__main__":
    inspect_chunks()
