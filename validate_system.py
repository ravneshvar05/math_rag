#!/usr/bin/env python
"""System validation and health check script."""

import sys
from pathlib import Path
import subprocess


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} - Need 3.9+")
        return False


def check_tesseract():
    """Check if Tesseract is installed."""
    print("\nChecking Tesseract OCR...")
    try:
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ {version} - OK")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ Tesseract not found")
    print("  Install: sudo apt-get install tesseract-ocr")
    return False


def check_dependencies():
    """Check if Python dependencies are installed."""
    print("\nChecking Python dependencies...")
    
    required = [
        'fitz',  # PyMuPDF
        'pdfplumber',
        'pytesseract',
        'PIL',  # Pillow
        'sentence_transformers',
        'faiss',
        'groq',
        'pandas',
        'numpy',
        'cv2',  # opencv-python
        'dotenv',
        'yaml',
        'tqdm',
        'tenacity',
        'loguru'
    ]
    
    missing = []
    for module in required:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - Missing")
            missing.append(module)
    
    if missing:
        print(f"\nMissing: {', '.join(missing)}")
        print("Install: pip install -r requirements.txt")
        return False
    
    return True


def check_env_file():
    """Check if .env file exists and has required keys."""
    print("\nChecking environment configuration...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("✗ .env file not found")
        print("  Create: cp .env.example .env")
        return False
    
    print("✓ .env file exists")
    
    # Check for required keys
    required_keys = ['GROQ_API_KEY', 'EMBEDDING_MODEL']
    content = env_file.read_text()
    
    for key in required_keys:
        if key in content and not content.split(key)[1].split('\n')[0].strip('=').strip():
            print(f"⚠ {key} is empty")
        elif key in content:
            print(f"✓ {key} configured")
        else:
            print(f"✗ {key} missing")
    
    return True


def check_directories():
    """Check if required directories exist."""
    print("\nChecking directory structure...")
    
    required_dirs = [
        'data/raw',
        'data/processed',
        'data/images',
        'data/tables',
        'logs'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ - Missing")
            all_exist = False
    
    if not all_exist:
        print("\nCreating missing directories...")
        for dir_path in required_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        print("✓ Directories created")
    
    return True


def check_config_file():
    """Check if config file exists."""
    print("\nChecking configuration file...")
    
    config_file = Path('config/config.yaml')
    if config_file.exists():
        print("✓ config/config.yaml exists")
        return True
    else:
        print("✗ config/config.yaml not found")
        return False


def test_imports():
    """Test key imports."""
    print("\nTesting key imports...")
    
    try:
        from app.pipeline import MathRAGPipeline
        print("✓ Pipeline import OK")
        
        from utils.math_utils import MathDetector
        print("✓ Math utils import OK")
        
        from utils.schema import ContentChunk
        print("✓ Schema import OK")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def run_basic_test():
    """Run basic functionality test."""
    print("\nRunning basic functionality test...")
    
    try:
        from utils.math_utils import MathDetector
        
        detector = MathDetector()
        
        # Test math detection
        test_text = "The integral \\int_0^1 x dx = 0.5"
        result = detector.contains_math(test_text)
        
        if result:
            print("✓ Math detection working")
            return True
        else:
            print("✗ Math detection failed")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def main():
    """Run all validation checks."""
    print("="*80)
    print("MATH RAG SYSTEM - VALIDATION")
    print("="*80)
    
    checks = [
        ("Python Version", check_python_version),
        ("Tesseract OCR", check_tesseract),
        ("Python Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Directory Structure", check_directories),
        ("Configuration File", check_config_file),
        ("Module Imports", test_imports),
        ("Basic Functionality", run_basic_test),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {name} - Error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ System is ready!")
        print("\nNext steps:")
        print("  1. Add your PDF textbooks to data/raw/")
        print("  2. Run: python -m app.index_document data/raw/your_book.pdf --class 11")
        print("  3. Query: python -m app.query")
        return 0
    else:
        print("\n✗ System has issues. Please fix the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())