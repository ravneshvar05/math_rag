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
        
        logger.info(f"Initialized chunker: {self.min_tokens}-{self.max_tokens} tokens")
    
    def chunk_document(
        self,
        pages: List[Dict[str, Any]],
        document_id: str,
        class_level: str
    ) -> List[ContentChunk]:
        """
        Chunk entire document into structured chunks.
        
        Args:
            pages: List of page data
            document_id: Document identifier
            class_level: Class level (11 or 12)
            
        Returns:
            List of content chunks
        """
        logger.info(f"Starting chunking for document: {document_id}")
        
        chunks = []
        current_chapter = {'number': 0, 'name': 'Introduction'}
        current_section = {'name': ''}
        
        for page in pages:
            page_chunks = self._chunk_page(
                page,
                document_id,
                class_level,
                current_chapter,
                current_section
            )
            chunks.extend(page_chunks)
            
            # Update chapter and section if found in page
            chapter = page.get('chapter')
            if chapter:
                current_chapter = chapter
            
            section = page.get('section')
            if section:
                current_section = section
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def _chunk_page(
        self,
        page: Dict[str, Any],
        document_id: str,
        class_level: str,
        chapter: Dict[str, Any],
        section: Dict[str, Any]
    ) -> List[ContentChunk]:
        """Chunk a single page."""
        chunks = []
        page_num = page.get('page_number', 0)
        text_blocks = page.get('blocks', [])
        images = page.get('images', [])
        tables = page.get('tables', [])
        
        # Group related blocks
        grouped_blocks = self._group_related_blocks(text_blocks)
        
        for block_group in grouped_blocks:
            chunk = self._create_chunk_from_blocks(
                block_group,
                document_id,
                class_level,
                chapter,
                section,
                page_num,
                images,
                tables
            )
            
            if chunk:
                chunks.append(chunk)
        
        # Handle standalone tables
        for table in tables:
            table_chunk = self._create_table_chunk(
                table,
                document_id,
                class_level,
                chapter,
                section
            )
            chunks.append(table_chunk)
        
        # Handle standalone images (diagrams without nearby text)
        for image in images:
            if not self._is_image_in_chunks(image, chunks):
                image_chunk = self._create_image_chunk(
                    image,
                    document_id,
                    class_level,
                    chapter,
                    section
                )
                chunks.append(image_chunk)
        
        return chunks
    
    def _group_related_blocks(self, blocks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group related text blocks together."""
        if not blocks:
            return []
        
        groups = []
        current_group = [blocks[0]]
        
        for i in range(1, len(blocks)):
            current_block = blocks[i]
            prev_block = blocks[i-1]
            
            # Check if blocks should be grouped
            if self._should_group_blocks(prev_block, current_block):
                current_group.append(current_block)
            else:
                groups.append(current_group)
                current_group = [current_block]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _should_group_blocks(self, block1: Dict[str, Any], block2: Dict[str, Any]) -> bool:
        """Determine if two blocks should be grouped."""
        text1 = block1.get('text', '')
        text2 = block2.get('text', '')
        
        # Don't split proofs
        if self.math_detector.is_proof(text1) or self.math_detector.is_proof(text2):
            return True
        
        # Don't split derivations
        if self.math_detector.is_derivation(text1) and self.math_detector.is_derivation(text2):
            return True
        
        # Check token count
        combined_tokens = self._estimate_tokens(text1 + text2)
        if combined_tokens > self.max_tokens:
            return False
        
        # Group if second block continues thought (starts with lowercase or connector)
        if text2 and text2[0].islower():
            return True
        
        connectors = ['therefore', 'thus', 'hence', 'so', 'then', 'also', 'similarly']
        if any(text2.lower().startswith(conn) for conn in connectors):
            return True
        
        return False
    
    def _create_chunk_from_blocks(
        self,
        blocks: List[Dict[str, Any]],
        document_id: str,
        class_level: str,
        chapter: Dict[str, Any],
        section: Dict[str, Any],
        page_num: int,
        page_images: List[ImageData],
        page_tables: List[TableData]
    ) -> Optional[ContentChunk]:
        """Create a content chunk from text blocks."""
        # Combine block texts
        text_content = "\n\n".join(block['text'] for block in blocks)
        
        if len(text_content.strip()) < 20:
            return None
        
        # Generate chunk ID
        chunk_id = str(uuid.uuid4())
        
        # Detect content type
        content_type_str = self.math_detector.detect_content_type(text_content)
        content_type = self._string_to_content_type(content_type_str)
        
        # Extract equations
        equations = self.math_detector.extract_equations(text_content)
        
        # Find related images (within proximity)
        related_images = self._find_related_images(blocks, page_images)
        
        # Find related tables
        related_tables = self._find_related_tables(blocks, page_tables)
        
        # Extract example number
        example_number = self._extract_example_info(text_content)
        
        # Create chunk
        chunk = ContentChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            class_level=class_level,
            chapter_number=chapter.get('number', 0),
            chapter_name=chapter.get('name', ''),
            section_name=section.get('name', ''),
            content_type=content_type,
            page_number=page_num,
            text_content=text_content,
            latex_equations=equations,
            has_equation=len(equations) > 0,
            equation_count=len(equations),
            images=related_images,
            has_image=len(related_images) > 0,
            image_count=len(related_images),
            tables=related_tables,
            has_table=len(related_tables) > 0,
            table_count=len(related_tables),
            contains_proof=self.math_detector.is_proof(text_content),
            contains_derivation=self.math_detector.is_derivation(text_content),
            is_definition='definition' in content_type_str,
            is_theorem='theorem' in content_type_str,
            is_example='example' in content_type_str,
            example_number=example_number,
            token_count=self._estimate_tokens(text_content),
            char_count=len(text_content),
            complexity_score=self.math_detector.calculate_math_density(text_content)
        )
        
        return chunk
    
    def _create_table_chunk(
        self,
        table: TableData,
        document_id: str,
        class_level: str,
        chapter: Dict[str, Any],
        section: Dict[str, Any]
    ) -> ContentChunk:
        """Create chunk for standalone table."""
        chunk_id = str(uuid.uuid4())
        
        chunk = ContentChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            class_level=class_level,
            chapter_number=chapter.get('number', 0),
            chapter_name=chapter.get('name', ''),
            section_name=section.get('name', ''),
            content_type=ContentType.TABLE,
            page_number=table.page_number,
            text_content=f"Table: {table.markdown_content}",
            tables=[table],
            has_table=True,
            table_count=1,
            token_count=self._estimate_tokens(table.markdown_content),
            char_count=len(table.markdown_content)
        )
        
        return chunk
    
    def _create_image_chunk(
        self,
        image: ImageData,
        document_id: str,
        class_level: str,
        chapter: Dict[str, Any],
        section: Dict[str, Any]
    ) -> ContentChunk:
        """Create chunk for standalone image."""
        chunk_id = str(uuid.uuid4())
        
        text_content = f"Image: {image.description}"
        if image.ocr_text:
            text_content += f"\n\nExtracted text: {image.ocr_text}"
        
        chunk = ContentChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            class_level=class_level,
            chapter_number=chapter.get('number', 0),
            chapter_name=chapter.get('name', ''),
            section_name=section.get('name', ''),
            content_type=ContentType.IMAGE,
            page_number=image.page_number,
            text_content=text_content,
            images=[image],
            has_image=True,
            image_count=1,
            token_count=self._estimate_tokens(text_content),
            char_count=len(text_content)
        )
        
        return chunk
    
    def _find_related_images(
        self,
        blocks: List[Dict[str, Any]],
        images: List[ImageData]
    ) -> List[ImageData]:
        """Find images related to text blocks based on position."""
        if not blocks or not images:
            return []
        
        related = []
        
        # Get bounding box of text blocks
        block_bboxes = [b.get('bbox') for b in blocks if b.get('bbox')]
        if not block_bboxes:
            return []
        
        # Simple proximity check
        for image in images:
            if image.bbox:
                # Check if image is near any block
                for block_bbox in block_bboxes:
                    if self._is_nearby(image.bbox, block_bbox, threshold=100):
                        related.append(image)
                        break
        
        return related
    
    def _find_related_tables(
        self,
        blocks: List[Dict[str, Any]],
        tables: List[TableData]
    ) -> List[TableData]:
        """Find tables related to text blocks."""
        # Similar to images
        if not blocks or not tables:
            return []
        
        related = []
        block_bboxes = [b.get('bbox') for b in blocks if b.get('bbox')]
        
        for table in tables:
            if table.bbox:
                for block_bbox in block_bboxes:
                    if self._is_nearby(table.bbox, block_bbox, threshold=150):
                        related.append(table)
                        break
        
        return related
    
    def _is_nearby(self, bbox1: List[float], bbox2: List[float], threshold: float) -> bool:
        """Check if two bounding boxes are nearby."""
        # Calculate distance between centers
        center1 = ((bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2)
        center2 = ((bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2)
        
        distance = ((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)**0.5
        
        return distance < threshold
    
    def _is_image_in_chunks(self, image: ImageData, chunks: List[ContentChunk]) -> bool:
        """Check if image is already included in chunks."""
        for chunk in chunks:
            for chunk_image in chunk.images:
                if chunk_image.image_id == image.image_id:
                    return True
        return False
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def _string_to_content_type(self, type_str: str) -> ContentType:
        """Convert string to ContentType enum."""
        type_map = {
            'definition': ContentType.DEFINITION,
            'theorem': ContentType.THEOREM,
            'proof': ContentType.PROOF,
            'derivation': ContentType.DERIVATION,
            'example': ContentType.EXAMPLE,
            'exercise': ContentType.EXERCISE,
            'solution': ContentType.SOLUTION,
            'table': ContentType.TABLE,
            'image': ContentType.IMAGE,
            'formula': ContentType.FORMULA,
        }
        
        return type_map.get(type_str, ContentType.TEXT)

    def _extract_example_info(self, text: str) -> Optional[str]:
        """Extract example number."""
        # Updated regex to handle potential newlines and various separators
        patterns = [
            r'Example\s*[:.-]?\s*(\d+(?:\.\d+)?)', 
            r'Example\s+[\r\n]+\s*(\d+(?:\.\d+)?)', # Handle header split across lines
            r'Ex\s*[:.-]?\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None