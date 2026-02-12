"""Content parser for detecting academic structure in textbooks."""

import re
from typing import List, Dict, Any, Optional, Tuple
from utils.schema import ContentType
from utils.math_utils import MathDetector
from utils.logging import get_logger

logger = get_logger(__name__)


class ContentParser:
    """Parse and structure textbook content."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize content parser.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.math_detector = MathDetector()
        
        # Load patterns from config
        self.content_markers = config.get('math_patterns', {}).get('content_type_markers', {})
        
        logger.info("Initialized content parser")
    
    def parse_document_structure(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse overall document structure.
        
        Args:
            pages: List of page data
            
        Returns:
            Structured document data
        """
        structure = {
            'chapters': [],
            'total_pages': len(pages),
            'content_units': []
        }
        
        current_chapter = None
        current_section = None
        
        for page in pages:
            page_text = page.get('text', '')
            page_num = page.get('page_number', 0)
            
            # Detect chapter
            chapter_info = self._detect_chapter(page_text, page_num)
            if chapter_info:
                current_chapter = chapter_info
                structure['chapters'].append(chapter_info)
                current_section = None
                logger.debug(f"Found chapter: {chapter_info['name']}")
            
            # Detect section
            section_info = self._detect_section(page_text, page_num)
            if section_info and current_chapter:
                section_info['chapter_number'] = current_chapter['number']
                current_section = section_info
            
            # Parse content units
            units = self._parse_page_content(page, current_chapter, current_section)
            structure['content_units'].extend(units)
        
        return structure
    
    def _detect_chapter(self, text: str, page_num: int) -> Optional[Dict[str, Any]]:
        """Detect chapter heading."""
        patterns = [
            r'CHAPTER\s+(\d+)\s*[:\-]?\s*([^\n]+)',
            r'Chapter\s+(\d+)\s*[:\-]?\s*([^\n]+)',
            r'(\d+)\.\s+([A-Z][^\n]{10,50})',  # Numbered heading
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'number': int(match.group(1)),
                    'name': match.group(2).strip(),
                    'start_page': page_num
                }
        
        return None
    
    def _detect_section(self, text: str, page_num: int) -> Optional[Dict[str, Any]]:
        """Detect section heading."""
        patterns = [
            r'(\d+\.\d+)\s+([A-Z][^\n]{10,50})',  # 1.1 Section Name
            r'Section\s+(\d+\.\d+)\s*[:\-]?\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return {
                    'number': match.group(1),
                    'name': match.group(2).strip(),
                    'start_page': page_num
                }
        
        return None
    
    def _parse_page_content(
        self,
        page: Dict[str, Any],
        chapter: Optional[Dict[str, Any]],
        section: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse content units from page."""
        units = []
        text = page.get('text', '')
        page_num = page.get('page_number', 0)
        
        # Split into paragraphs
        paragraphs = self._split_paragraphs(text)
        
        for para in paragraphs:
            if len(para.strip()) < 20:  # Skip very short paragraphs
                continue
            
            # Detect content type
            content_type = self._detect_content_type(para)
            
            # Check for special content
            is_proof = self.math_detector.is_proof(para)
            is_derivation = self.math_detector.is_derivation(para)
            contains_math = self.math_detector.contains_math(para)
            
            # Extract exercise info
            exercise_info = self._extract_exercise_info(para)
            
            # Extract example info
            example_number = self._extract_example_info(para)
            
            unit = {
                'text': para,
                'page_number': page_num,
                'content_type': content_type,
                'is_proof': is_proof,
                'is_derivation': is_derivation,
                'contains_math': contains_math,
                'chapter': chapter,
                'section': section,
                'exercise_info': exercise_info,
                'example_number': example_number
            }
            
            units.append(unit)
        
        return units
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into logical paragraphs."""
        # Split on double newlines first
        paragraphs = re.split(r'\n\s*\n', text)
        
        result = []
        for para in paragraphs:
            para = para.strip()
            if para:
                # Further split long paragraphs at sentence boundaries if needed
                if len(para) > 1000:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_para = ""
                    
                    for sentence in sentences:
                        if len(current_para) + len(sentence) < 800:
                            current_para += sentence + " "
                        else:
                            if current_para:
                                result.append(current_para.strip())
                            current_para = sentence + " "
                    
                    if current_para:
                        result.append(current_para.strip())
                else:
                    result.append(para)
        
        return result
    
    def _detect_content_type(self, text: str) -> str:
        """Detect content type from text."""
        text_lower = text.lower()
        
        # Check each content type marker
        for content_type, markers in self.content_markers.items():
            for marker in markers:
                if re.search(marker, text, re.IGNORECASE):
                    return content_type
        
        # Use math detector for additional detection
        detected = self.math_detector.detect_content_type(text)
        if detected != 'text':
            return detected
        
        return 'text'
    
    def _extract_exercise_info(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract exercise number and question details."""
        # Pattern for exercise numbers
        patterns = [
            r'Exercise\s+(\d+)\.(\d+)',
            r'Question\s+(\d+)',
            r'Q\.?\s*(\d+)',
            r'Problem\s+(\d+)',
            r'^(\d+)\.',  # Just a number at start
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return {
                        'exercise_number': int(groups[0]),
                        'question_number': groups[1]
                    }
                else:
                    return {
                        'exercise_number': None,
                        'question_number': groups[0]
                    }
        
        return None
    
        return None
    
    def _extract_example_info(self, text: str) -> Optional[str]:
        """Extract example number."""
        patterns = [
            r'Example\s+(\d+(?:\.\d+)?)',
            r'Ex\.\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def detect_proof_boundaries(self, text: str) -> List[Tuple[int, int]]:
        """
        Detect start and end positions of proofs.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (start, end) positions
        """
        boundaries = []
        
        # Find proof starts
        proof_start_pattern = r'\b(Proof|PROOF|Proof:)\b'
        proof_end_pattern = r'\b(Q\.E\.D\.|∎|Hence proved|Therefore proved)\b'
        
        starts = [m.start() for m in re.finditer(proof_start_pattern, text, re.IGNORECASE)]
        ends = [m.end() for m in re.finditer(proof_end_pattern, text, re.IGNORECASE)]
        
        # Match starts with ends
        for start in starts:
            # Find next end after this start
            matching_end = None
            for end in ends:
                if end > start:
                    matching_end = end
                    break
            
            if matching_end:
                boundaries.append((start, matching_end))
            else:
                # No explicit end, take next 500 chars or next proof
                next_start = None
                for s in starts:
                    if s > start:
                        next_start = s
                        break
                
                end_pos = next_start if next_start else min(start + 500, len(text))
                boundaries.append((start, end_pos))
        
        return boundaries
    
    def split_by_logical_steps(self, text: str) -> List[str]:
        """
        Split derivation or proof into logical steps.
        
        Args:
            text: Derivation text
            
        Returns:
            List of step texts
        """
        # Split on step indicators
        step_patterns = [
            r'Step\s+\d+:',
            r'\(\d+\)',  # (1), (2), etc.
            r'^\d+\.',   # 1., 2., etc. at line start
        ]
        
        steps = []
        current_step = ""
        lines = text.split('\n')
        
        for line in lines:
            is_new_step = False
            for pattern in step_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_new_step = True
                    break
            
            if is_new_step and current_step:
                steps.append(current_step.strip())
                current_step = line
            else:
                current_step += "\n" + line
        
        if current_step:
            steps.append(current_step.strip())
        
        return steps if len(steps) > 1 else [text]