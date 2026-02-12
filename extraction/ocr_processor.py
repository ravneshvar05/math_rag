"""OCR module for extracting text from images."""

import pytesseract
from PIL import Image
from pathlib import Path
from typing import Optional, Dict, Any
import cv2
import numpy as np
from utils.logging import get_logger

logger = get_logger(__name__)


class OCRProcessor:
    """Process images with OCR to extract text."""
    
    def __init__(self, languages: list = None):
        """
        Initialize OCR processor.
        
        Args:
            languages: List of languages for OCR (default: ['eng'])
        """
        self.languages = languages or ['eng']
        self.config = '--oem 3 --psm 6'  # LSTM OCR Engine, assume uniform text block
        
        logger.info(f"Initialized OCR processor with languages: {self.languages}")
    
    def extract_text(self, image_path: str, preprocess: bool = True) -> str:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to image file
            preprocess: Whether to preprocess image
            
        Returns:
            Extracted text
        """
        try:
            # Load image
            img = Image.open(image_path)
            
            # Preprocess if needed
            if preprocess:
                img = self._preprocess_image(img)
            
            # Perform OCR
            text = pytesseract.image_to_string(
                img,
                lang='+'.join(self.languages),
                config=self.config
            )
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            return ""
    
    def extract_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract detailed data from image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with OCR data including confidence
        """
        try:
            img = Image.open(image_path)
            img = self._preprocess_image(img)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(
                img,
                lang='+'.join(self.languages),
                output_type=pytesseract.Output.DICT
            )
            
            return data
            
        except Exception as e:
            logger.error(f"OCR data extraction failed for {image_path}: {e}")
            return {}
    
    def contains_text(self, image_path: str, threshold: int = 10) -> bool:
        """
        Check if image contains meaningful text.
        
        Args:
            image_path: Path to image file
            threshold: Minimum character count to consider as text
            
        Returns:
            True if image contains text
        """
        text = self.extract_text(image_path)
        return len(text.strip()) >= threshold
    
    def get_confidence(self, image_path: str) -> float:
        """
        Get average OCR confidence score.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Average confidence (0-100)
        """
        try:
            data = self.extract_data(image_path)
            confidences = [conf for conf in data.get('conf', []) if conf != -1]
            
            if confidences:
                return sum(confidences) / len(confidences)
            return 0.0
            
        except Exception as e:
            logger.warning(f"Failed to get confidence for {image_path}: {e}")
            return 0.0
    
    def _preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results.
        
        Args:
            img: PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert PIL to OpenCV format
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        # Convert back to PIL
        img_pil = Image.fromarray(denoised)
        
        return img_pil
    
    def is_mathematical_content(self, image_path: str) -> bool:
        """
        Detect if image contains mathematical content.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if mathematical content detected
        """
        text = self.extract_text(image_path)
        
        math_indicators = [
            r'\d+[\+\-\*/=]\d+',  # Basic operations
            r'[∫∑∏√]',  # Math symbols
            r'[α-ω]',  # Greek letters
            r'\\frac',  # LaTeX
            r'\\int',
            r'[xyz]\s*[=<>]',  # Variables
        ]
        
        import re
        for indicator in math_indicators:
            if re.search(indicator, text):
                return True
        
        return False


class ImageDescriptionGenerator:
    """Generate descriptions for images (placeholder for future ML model)."""
    
    def __init__(self):
        """Initialize description generator."""
        logger.info("Initialized image description generator")
    
    def generate_description(self, image_path: str, image_type: str) -> str:
        """
        Generate description for image.
        
        Args:
            image_path: Path to image
            image_type: Type of image (diagram, graph, etc.)
            
        Returns:
            Generated description
        """
        # Placeholder - can be enhanced with CLIP or other vision models
        
        img = Image.open(image_path)
        width, height = img.size
        
        descriptions = {
            'diagram': f"Diagram illustration (size: {width}x{height})",
            'graph': f"Graph or chart (size: {width}x{height})",
            'equation': f"Mathematical equation image (size: {width}x{height})",
            'text': f"Text image (size: {width}x{height})",
        }
        
        return descriptions.get(image_type, f"Image (size: {width}x{height})")
    
    def enhance_with_context(self, description: str, context: str) -> str:
        """
        Enhance description with surrounding text context.
        
        Args:
            description: Base description
            context: Surrounding text
            
        Returns:
            Enhanced description
        """
        # Extract topic from context
        import re
        
        # Look for chapter/section names
        chapter_match = re.search(r'chapter\s+\d+[:\s]+([^\n]+)', context, re.IGNORECASE)
        if chapter_match:
            topic = chapter_match.group(1).strip()
            description += f" related to {topic}"
        
        return description