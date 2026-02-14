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
            # Detect layout
            split_x = self._detect_columns(page)
            
            # Extract text (hybrid)
            page_data = self._extract_page_hybrid(page, page_num + 1)
            result['pages'].append(page_data)
            
            # Extract diagrams
            page_images = self._extract_images_and_diagrams(page, page_num + 1, split_x)
            result['images'].extend(page_images)
            
            # Extract tables
            page_tables = self._extract_tables(page, page_num + 1)
            result['tables'].extend(page_tables)
            
            # Attach images/tables to page data for easier chunking access
            page_data['images'] = page_images
            page_data['tables'] = page_tables
            
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


    def _detect_columns(self, page) -> float:
        """
        Detect if page is two-column and return split point.
        Returns 0 if single column, or x-coordinate of split if two-column.
        """
        # Get all text blocks
        blocks = page.get_text("blocks")
        if not blocks:
            return 0
            
        # Analyze horizontal distribution of blocks
        # If we see a distinct gap in the middle, it's likely two-column
        page_width = page.rect.width
        mid_point = page_width / 2
        
        # Check central gutter (10% of width around center)
        gutter_start = mid_point - (page_width * 0.05)
        gutter_end = mid_point + (page_width * 0.05)
        
        blocks_in_gutter = [
            b for b in blocks 
            if b[0] < gutter_end and b[2] > gutter_start
        ]
        
        # If few blocks cross the center, it's likely two columns
        # (Allow for some headers/footers to cross)
        if len(blocks_in_gutter) < len(blocks) * 0.2:
            return mid_point
            
        return 0

    def _get_diagram_bbox(self, page, caption_block, split_x: float):
        """Finds diagrams strictly within the same column as the caption."""
        import fitz
        caption_rect = fitz.Rect(caption_block[:4])
        
        # Determine column context
        is_left_col = True
        if split_x > 0:
            is_left_col = caption_rect.x0 < split_x
        
        # Define Column Boundaries to prevent bleed-over
        col_min_x = 0
        col_max_x = page.rect.width
        
        if split_x > 0:
            col_min_x = 0 if is_left_col else split_x
            col_max_x = split_x if is_left_col else page.rect.width
        
        # Define Vertical Search Area (Above the caption)
        # Look up to 300 units above
        search_area = fitz.Rect(col_min_x, max(0, caption_rect.y0 - 300), col_max_x, caption_rect.y0)
        
        # Filter drawings that stay WITHIN this specific column
        drawings = []
        for d in page.get_drawings():
            d_rect = d["rect"]
            
            # Ignore page-sized backgrounds/borders/layout containers
            # If a single drawing is very large (e.g. > 50% of page height), it's likely a container
            if d_rect.width > page.rect.width * 0.9 or d_rect.height > page.rect.height * 0.5:
                continue
                
            if (d_rect.intersects(search_area) and 
                d_rect.x0 >= col_min_x and 
                d_rect.x1 <= col_max_x):
                drawings.append(d_rect)
        
        if not drawings:
            return None
            
        # Merge all drawing rects
        diagram_box = drawings[0]
        for d_rect in drawings[1:]:
            diagram_box |= d_rect
            
        # Add padding
        return diagram_box + (-5, -5, 5, 5)

    def _extract_images_and_diagrams(self, page, page_number: int, split_x: float) -> List[Dict[str, Any]]:
        """Extract images and diagrams based on captions."""
        images = []
        blocks = page.get_text("blocks")
        
        # Regular expressions for captions
        caption_patterns = [
            r'^Fig(?:ure)?\.?\s*(\d+(?:\.\d+)?)',  # Fig. 1.1 or Figure 1.1
            r'^Table\s*(\d+(?:\.\d+)?)',           # Table 1.1 (though usually tables are handled separately)
        ]
        
        for block in blocks:
            text = block[4].strip()
            # Check if block is a caption
            is_caption = False
            match = None
            
            for pattern in caption_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    is_caption = True
                    break
            
            if is_caption and match:
                # It's a caption, look for the diagram above it
                bbox = self._get_diagram_bbox(page, block, split_x)
                
                if bbox:
                    # Generate ID
                    fig_id = match.group(1).replace('.', '_')
                    image_filename = f"fig_{fig_id}_p{page_number}.png"
                    image_path = self.output_dir / "images" / image_filename
                    image_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Save image
                    # Use higher zoom for quality
                    pix = page.get_pixmap(clip=bbox, matrix=fitz.Matrix(3, 3))
                    pix.save(str(image_path))
                    
                    images.append({
                        'image_id': f"fig_{fig_id}",
                        'image_path': str(image_path),
                        'image_type': 'diagram',
                        'description': text,  # Caption is the description
                        'page_number': page_number,
                        'bbox': [bbox.x0, bbox.y0, bbox.x1, bbox.y1]
                    })
                    logger.info(f"Extracted diagram {fig_id} from page {page_number}")

        return images

    def _extract_tables(self, page, page_number: int) -> List[Dict[str, Any]]:
        """Extract tables using PyMuPDF's find_tables."""
        tables_data = []
        
        # Find tables
        tables = page.find_tables()
        
        for i, table in enumerate(tables):
            # Extract content to Markdown
            md_content = table.to_markdown()
            
            # Extract to CSV
            import csv
            import io
            csv_output = io.StringIO()
            writer = csv.writer(csv_output)
            writer.writerows(table.extract())
            csv_content = csv_output.getvalue()
            
            # Generate ID
            table_id = f"table_p{page_number}_{i+1}"
            
            # Save table image for visual verification (optional)
            # bbox = table.bbox
            # ... coding to save image ...
            
            tables_data.append({
                'table_id': table_id,
                'table_path': '',  # Placeholder if we save image later
                'markdown_content': md_content,
                'csv_content': csv_content,
                'num_rows': table.row_count,
                'num_cols': table.col_count,
                'has_header': table.header.external,
                'page_number': page_number,
                'bbox': [table.bbox[0], table.bbox[1], table.bbox[2], table.bbox[3]]
            })
            
        return tables_data

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

