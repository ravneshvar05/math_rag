import sys
from pathlib import Path
import logging
import fitz

# Add project root to path
sys.path.append(str(Path.cwd()))

from extraction.pdf_extractor import PDFExtractor
from utils.logging import get_logger

logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

def run_extraction():
    pdf_path = "data/raw/math_class_11.pdf"
    output_dir = "data/processed_verification"
    
    extractor = PDFExtractor(pdf_path, output_dir)
    
    # Manually run extraction on page 11 (index 10) logic
    doc = fitz.open(pdf_path)
    page_num = 10
    page = doc[page_num]
    
    split_x = extractor._detect_columns(page)
    images = extractor._extract_images_and_diagrams(page, page_num + 1, split_x)
    
    logger.info(f"Extracted {len(images)} images from page {page_num+1}")
    for img in images:
        logger.info(f"Image: {img['image_id']} Path: {img['image_path']}")

if __name__ == "__main__":
    run_extraction()
