import fitz  # PyMuPDF
import logging
from utils.logging import get_logger
from pathlib import Path
from typing import Dict, Any, List

logger = get_logger(__name__)


class PDFExtractor:
    def __init__(self, pdf_path: str, output_dir: str):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_all(self) -> Dict[str, Any]:
        """
        Extract all content from PDF.
        """
        logger.info(f"Extracting content from {self.pdf_path}")
        
        # Open PDF
        doc = fitz.open(self.pdf_path)
        
        result = {
            'pages': [],
            'images': [],
            'tables': [],
            'total_pages': len(doc)
        }
        
        for page_num, page in enumerate(doc):
            # Extract text
            text = page.get_text()
            
            # Extract blocks
            blocks_raw = page.get_text("blocks")
            blocks = []
            for b in blocks_raw:
                # b is (x0, y0, x1, y1, text, block_no, block_type)
                if b[6] == 0:  # Text block
                    blocks.append({
                        'bbox': b[:4],
                        'text': b[4],
                        'type': 'text'
                    })
            
            result['pages'].append({
                'page_number': page_num + 1,
                'text': text,
                'blocks': blocks
            })
            
        return result

    def extract_text(self, file_path: str) -> str:
        logger.info(f"Extracting text from {file_path}")
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

