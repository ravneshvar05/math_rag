import os
import sys
import importlib
from pathlib import Path

def verify_imports(root_dir):
    print(f"Verifying imports in {root_dir}...")
    success_count = 0
    error_count = 0
    
    # Ensure root is in sys.path
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    
    for root, dirs, files in os.walk(root_dir):
        if 'venv' in root or '__pycache__' in root or '.git' in root:
            continue
            
        for file in files:
            if file == "setup.py" or file == "validate_system.py" or file == "verify_all_imports.py":
                continue
                
            if file.endswith(".py"):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(root_dir)
                
                # Convert path to module name
                parts = list(rel_path.parts)
                parts[-1] = parts[-1][:-3] # remove .py
                
                if parts[-1] == "__init__":
                    parts.pop() # remove __init__
                
                if not parts: # Root __init__.py? (Unlikely)
                    print(f"Skipping {file_path}")
                    continue
                    
                module_name = ".".join(parts)
                
                try:
                    print(f"Checking {module_name}...", end="", flush=True)
                    importlib.import_module(module_name)
                    print(" OK")
                    success_count += 1
                except Exception as e:
                    print(f" FAILED: {e}")
                    error_count += 1

    print("\n" + "="*30)
    print(f"Verification Complete.")
    print(f"Passed: {success_count}")
    print(f"Failed: {error_count}")
    print("="*30)

if __name__ == "__main__":
    project_root = Path(__file__).parent
    verify_imports(project_root)
