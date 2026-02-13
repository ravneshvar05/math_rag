"""Structure-aware chunking for mathematics content."""

from typing import List, Dict, Any, Optional
from utils.schema import ContentChunk, ContentType, ImageData, TableData, EquationData
from utils.math_utils import MathDetector, EquationCleaner
from utils.logging import get_logger
import uuid
import re

logger = get_logger(__name__)


class StructureAwareChunker:
    """Create structure-aware chunks from extracted content."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize chunker.
        
        Args:
            config: Chunking configuration
        """
        self.min_tokens = config.get('min_tokens', 200)
        self.max_tokens = config.get('max_tokens', 800)
        self.overlap_tokens = config.get('overlap_tokens', 50)
        self.preserve_units = config.get('preserve_units', ['proof', 'derivation', 'theorem'])
        
        self.math_detector = MathDetector()
        self.equation_cleaner = EquationCleaner()
        
        logger.info(f"Initialized StructureAwareChunker with max_tokens={self.max_tokens}")
    
    def chunk_document(
        self,
        pages: List[Dict[str, Any]],
        document_id: str,
        class_level: str
    ) -> List[ContentChunk]:
        """
        Chunk entire document into structured chunks with cross-page grouping.
        
        Args:
            pages: List of page data
            document_id: Document identifier
            class_level: Class level (11 or 12)
            
        Returns:
            List of content chunks
        """
        logger.info(f"Starting smart chunking for document: {document_id}")
        
        chunks = []
        current_chapter = {'number': 0, 'name': 'Introduction'}
        current_section = {'name': ''}
        
        # State for cross-page exercise/example collection
        collecting_exercise = False
        exercise_buffer = {
            'text': '',
            'number': '',
            'start_page': 0,
            'type': 'exercise'  # or 'example'
        }
        
        for page_idx, page in enumerate(pages):
            page_num = page.get('page_number', page_idx + 1)
            page_text = page.get('text', '')
            blocks = page.get('blocks', [])
            
            # Check for exercise/example headers
            exercise_match = re.search(r'EXERCISE\s+(\d+\.\d+)', page_text, re.IGNORECASE)
            example_match = re.search(r'Example\s+(\d+)', page_text, re.IGNORECASE)
            
            # If we find a new exercise/example header
            if exercise_match or example_match:
                # Save previous collection if exists
                if collecting_exercise and exercise_buffer['text']:
                    chunk = self._create_collection_chunk(
                        exercise_buffer,
                        document_id,
                        class_level,
                        current_chapter,
                        current_section
                    )
                    if chunk:
                        chunks.append(chunk)
                
                # Start new collection
                if exercise_match:
                    exercise_buffer = {
                        'text': page_text,
                        'number': exercise_match.group(1),
                        'start_page': page_num,
                        'type': 'exercise'
                    }
                    collecting_exercise = True
                    logger.info(f"Started collecting Exercise {exercise_match.group(1)} from page {page_num}")
                    
                elif example_match:
                    exercise_buffer = {
                        'text': page_text,
                        'number': example_match.group(1),
                        'start_page': page_num,
                        'type': 'example'
                    }
                    collecting_exercise = True
                    logger.info(f"Started collecting Example {example_match.group(1)} from page {page_num}")
            
            elif collecting_exercise:
                # Continue collecting until we hit another exercise/example or significant break
                # Check if we've hit a new major section
                if re.search(r'(MISCELLANEOUS|SUMMARY|CHAPTER)', page_text, re.IGNORECASE):
                    # Stop collecting and save
                    chunk = self._create_collection_chunk(
                        exercise_buffer,
                        document_id,
                        class_level,
                        current_chapter,
                        current_section
                    )
                    if chunk:
                        chunks.append(chunk)
                    collecting_exercise = False
                else:
                    # Add to buffer
                    exercise_buffer['text'] += '\n\n' + page_text
            
            else:
                # Regular chunking for non-exercise/example content
                page_chunks = self._chunk_page(
                    page,
                    document_id,
                    class_level,
                    current_chapter,
                    current_section
                )
                chunks.extend(page_chunks)
            
            # Update chapter and section if found
            chapter_match = re.search(r'CHAPTER\s+(\d+)', page_text, re.IGNORECASE)
            if chapter_match:
                current_chapter = {'number': int(chapter_match.group(1)), 'name': 'Chapter ' + chapter_match.group(1)}
        
        # Save any remaining collection
        if collecting_exercise and exercise_buffer['text']:
            chunk = self._create_collection_chunk(
                exercise_buffer,
                document_id,
                class_level,
                current_chapter,
                current_section
            )
            if chunk:
                chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from document (with smart grouping)")
        return chunks
    
    def _create_collection_chunk(
        self,
        buffer: Dict[str, Any],
        document_id: str,
        class_level: str,
        chapter: Dict[str, Any],
        section: Dict[str, Any]
    ) -> Optional[ContentChunk]:
        """Create a chunk from collected exercise/example content."""
        if not buffer['text'].strip():
            return None
        
        chunk_type = ContentType.EXERCISE if buffer['type'] == 'exercise' else ContentType.EXAMPLE
        
        # Extract equations from text
        equations = self.math_detector.extract_equations(buffer['text'])
        
        chunk = ContentChunk(
            chunk_id=str(uuid.uuid4()),
            document_id=document_id,
            class_level=class_level,
            chapter_number=chapter.get('number', 0),
            chapter_name=chapter.get('name', ''),
            section_name=section.get('name', ''),
            content_type=chunk_type,
            text_content=buffer['text'],
            page_number=buffer['start_page'],
            latex_equations=equations,
            images=[],
            tables=[],
            example_number=buffer['number'] if buffer['type'] == 'example' else None,
            exercise_number=buffer['number'] if buffer['type'] == 'exercise' else None
        )
        
        return chunk
    
    def _chunk_page(
        self,
        page: Dict[str, Any],
        document_id: str,
        class_level: str,
        chapter: Dict[str, Any],
        section: Dict[str, Any]
    ) -> List[ContentChunk]:
        """Chunk a single page (fallback for regular content)."""
        chunks = []
        page_num = page.get('page_number', 0)
        text = page.get('text', '')
        
        # Simple chunking for non-exercise content
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        
        current_text = ""
        for para in paragraphs:
            if not para.strip():
                continue
            
            # Estimate token count (rough: word count * 1.3)
            current_tokens = len(current_text.split()) * 1.3
            para_tokens = len(para.split()) * 1.3
            
            if current_tokens + para_tokens > self.max_tokens and current_text:
                # Create chunk
                chunk = self._create_simple_chunk(
                    current_text,
                    document_id,
                    class_level,
                    chapter,
                    section,
                    page_num
                )
                if chunk:
                    chunks.append(chunk)
                current_text = para
            else:
                current_text += '\n\n' + para if current_text else para
        
        # Create final chunk
        if current_text.strip():
            chunk = self._create_simple_chunk(
                current_text,
                document_id,
                class_level,
                chapter,
                section,
                page_num
            )
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _create_simple_chunk(
        self,
        text: str,
        document_id: str,
        class_level: str,
        chapter: Dict[str, Any],
        section: Dict[str, Any],
        page_num: int
    ) -> Optional[ContentChunk]:
        """Create a simple text chunk."""
        if not text.strip():
            return None
        
        # Detect content type
        content_type_str = self.math_detector.detect_content_type(text)
        content_type = self._map_content_type(content_type_str)
        
        # Extract equations
        equations = self.math_detector.extract_equations(text)
        
        chunk = ContentChunk(
            chunk_id=str(uuid.uuid4()),
            document_id=document_id,
            class_level=class_level,
            chapter_number=chapter.get('number', 0),
            chapter_name=chapter.get('name', ''),
            section_name=section.get('name', ''),
            content_type=content_type,
            text_content=text,
            page_number=page_num,
            latex_equations=equations,
            images=[],
            tables=[]
        )
        
        return chunk
    
    def _map_content_type(self, type_str: str) -> ContentType:
        """Map string content type to ContentType enum."""
        mapping = {
            'definition': ContentType.DEFINITION,
            'theorem': ContentType.THEOREM,
            'proof': ContentType.PROOF,
            'example': ContentType.EXAMPLE,
            'exercise': ContentType.EXERCISE,
            'solution': ContentType.SOLUTION,
            'derivation': ContentType.DERIVATION,
        }
        return mapping.get(type_str, ContentType.TEXT)
