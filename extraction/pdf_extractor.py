import fitz  # PyMuPDF
import logging
from utils.logging import get_logger
from pathlib import Path
from typing import Dict, Any, List
import re
import pytesseract
from PIL import Image
import io

logger = get_logger(__name__)


class PDFExtractor:
    def __init__(self, pdf_path: str, output_dir: str):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Tesseract configuration for mathematical text
        self.tesseract_config = '--psm 6 --oem 3'  # Single block, best OCR engine
        
    def extract_all(self) -> Dict[str, Any]:
        """
        Extract all content from PDF with hybrid approach:
        - Regular text blocks: PyMuPDF
        - Formula blocks: Tesseract OCR
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
            page_data = self._extract_page_hybrid(page, page_num + 1)
            result['pages'].append(page_data)
            
        return result
    
    def _extract_page_hybrid(self, page, page_number: int) -> Dict[str, Any]:
        """
        Extract page using hybrid approach: regular text + OCR for formulas.
        """
        # Get blocks with bounding boxes
        blocks_raw = page.get_text("blocks")
        
        reconstructed_text_parts = []
        processed_blocks = []
        
        for block in blocks_raw:
            if block[6] != 0:  # Skip non-text blocks
                continue
                
            bbox = block[:4]
            block_text = block[4]
            
            # Detect if this block contains dense mathematical formulas
            if self._is_formula_heavy_block(block_text):
                logger.debug(f"Formula block detected on page {page_number}: {block_text[:50]}...")
                
                # Try OCR extraction for better formula preservation
                try:
                    ocr_text = self._extract_formula_with_ocr(page, bbox)
                    if ocr_text and len(ocr_text.strip()) > 0:
                        reconstructed_text_parts.append(ocr_text)
                        processed_blocks.append({
                            'bbox': bbox,
                            'text': ocr_text,
                            'type': 'formula_ocr'
                        })
                    else:
                        # Fallback to regular extraction
                        reconstructed_text_parts.append(block_text)
                        processed_blocks.append({
                            'bbox': bbox,
                            'text': block_text,
                            'type': 'text'
                        })
                except Exception as e:
                    logger.warning(f"OCR failed for block, using fallback: {e}")
                    reconstructed_text_parts.append(block_text)
                    processed_blocks.append({
                        'bbox': bbox,
                        'text': block_text,
                        'type': 'text'
                    })
            else:
                # Regular text block - use PyMuPDF extraction
                reconstructed_text_parts.append(block_text)
                processed_blocks.append({
                    'bbox': bbox,
                    'text': block_text,
                    'type': 'text'
                })
        
        return {
            'page_number': page_number,
            'text': '\n'.join(reconstructed_text_parts),
            'blocks': processed_blocks
        }
    
    def _is_formula_heavy_block(self, text: str) -> bool:
        """
        Detect if a text block is formula-heavy using heuristics.
        """
        if not text or len(text.strip()) < 10:
            return False
        
        # Count mathematical symbols
        math_symbols = ['=', '±', '×', '÷', '∫', '∑', '∏', '√', '∞', '∂', '∇',
                       '≤', '≥', '≠', '≈', '→', '←', '↔', '⇒', '⇐', '⇔',
                       'α', 'β', 'γ', 'δ', 'θ', 'λ', 'μ', 'σ', 'π', 'ω', 'Δ']
        
        math_count = sum(text.count(sym) for sym in math_symbols)
        
        # Count common math functions
        math_functions = ['sin', 'cos', 'tan', 'log', 'ln', 'exp', 'lim']
        function_count = sum(len(re.findall(rf'\b{func}\b', text, re.IGNORECASE)) for func in math_functions)
        
        # Fraction-like patterns (numerator over denominator)
        # Detect multiple short lines which might indicate stacked fractions
        lines = text.strip().split('\n')
        short_lines = [l for l in lines if len(l.strip()) < 30 and len(l.strip()) > 0]
        
        # Heuristic: Consider formula-heavy if:
        # 1. High density of math symbols (>3 symbols)
        # 2. Or multiple math functions (>2)
        # 3. Or many short lines suggesting stacked layout (>3)
        
        is_formula = (
            math_count >= 3 or 
            function_count >= 2 or 
            (len(short_lines) >= 3 and math_count >= 1)
        )
        
        return is_formula
    
    def _extract_formula_with_ocr(self, page, bbox: tuple) -> str:
        """
        Extract formula region using OCR for better spatial layout preservation.
        
        Args:
            page: PyMuPDF page object
            bbox: Bounding box (x0, y0, x1, y1)
            
        Returns:
            OCR-extracted text
        """
        try:
            # Render the specific region as an image with higher resolution
            # Increase resolution significantly for better OCR quality
            zoom = 3.0  # 3x resolution (was 2x)
            mat = fitz.Matrix(zoom, zoom)
            
            # Get the region
            rect = fitz.Rect(bbox)
            pix = page.get_pixmap(matrix=mat, clip=rect)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            
            # Enhanced preprocessing for mathematical text
            # 1. Convert to grayscale
            image = image.convert('L')
            
            # 2. Resize for optimal Tesseract performance (300 DPI equivalent)
            # Tesseract works best at 300 DPI
            width, height = image.size
            if width < 600:  # If image is too small, scale up
                scale = 600 / width
                new_size = (int(width * scale), int(height * scale))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # 3. Enhance contrast and binarize with adaptive threshold
            # This helps Tesseract recognize characters better
            from PIL import ImageEnhance, ImageFilter
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)  # Increase contrast
            
            # Apply slight sharpening
            image = image.filter(ImageFilter.SHARPEN)
            
            # Run Tesseract OCR with math-optimized config
            # PSM 6: Uniform block of text (good for formulas)
            # --oem 1: Use LSTM OCR Engine (best quality)
            ocr_config = '--psm 6 --oem 1 -c preserve_interword_spaces=1'
            ocr_text = pytesseract.image_to_string(image, config=ocr_config)
            
            return ocr_text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""


    def extract_text(self, file_path: str) -> str:
        """
        Extract text using hybrid method.
        """
        logger.info(f"Extracting text from {file_path}")
        extraction_result = self.extract_all()
        
        text_parts = []
        for page_data in extraction_result['pages']:
            text_parts.append(page_data['text'])
        
        return '\n\n'.join(text_parts)
