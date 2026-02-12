
import sys
import fitz
import re
import os

# Force UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def scan_patterns():
    folder = "data/raw"
    files = [f for f in os.listdir(folder) if f.endswith(".pdf")]
    
    print(f"Scanning {len(files)} files for 'Exercise' or 'Example' patterns...")
    
    for filename in files:
        path = os.path.join(folder, filename)
        print(f"\nScanning: {filename}")
        try:
            doc = fitz.open(path)
            for page in doc:
                text = page.get_text()
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    
                    # Check for Exercise variants
                    if "EXERCISE" in line.upper():
                        print(f"  Found Exercise Line: '{line}'")
                        
                    # Check for Example variants
                    if "EXAMPLE" in line.upper() and len(line) < 50:
                         # Filter out long sentences containing "example"
                         if re.match(r'^\s*Example', line, re.IGNORECASE):
                             print(f"  Found Example Header: '{line}'")
                             
        except Exception as e:
            print(f"Error scanning {filename}: {e}")

if __name__ == "__main__":
    scan_patterns()
