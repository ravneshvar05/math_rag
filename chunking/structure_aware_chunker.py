"""Structure-aware chunking for mathematics content."""

from typing import List, Dict, Any, Optional
from utils.schema import ContentChunk, ContentType, ImageData, TableData, EquationData, ImageType
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
            'type': 'exercise',  # or 'example'
            'images': []
        }
        
        for page_idx, page in enumerate(pages):
            page_num = page.get('page_number', page_idx + 1)
            page_text = page.get('text', '')
            blocks = page.get('blocks', [])
            
            # Retrieve page-level images and tables
            current_page_images = page.get('images', [])
            current_page_tables = page.get('tables', [])
            
            # Check for exercise/example headers
            exercise_match = re.search(r'EXERCISE\s+(\d+\.\d+)', page_text, re.IGNORECASE)
            example_match = re.search(r'Example\s+(\d+)', page_text, re.IGNORECASE)
            
            # If we find a new exercise/example header
            if exercise_match or example_match:
                # Save previous collection if exists
                if collecting_exercise and exercise_buffer['text']:
                    collection_chunks = self._create_collection_chunk(
                        exercise_buffer,
                        document_id,
                        class_level,
                        current_chapter,
                        current_section,
                        # Pass buffered images
                        page_images=exercise_buffer['images'], 
                        page_tables=current_page_tables
                    )
                    if collection_chunks:
                        chunks.extend(collection_chunks)
                
                # Start new collection
                if exercise_match:
                    exercise_buffer = {
                        'text': page_text,
                        'number': exercise_match.group(1),
                        'start_page': page_num,
                        'type': 'exercise',
                        'images': []
                    }
                    # Init images with current page's images
                    exercise_buffer['images'].extend(current_page_images)
                    collecting_exercise = True
                    logger.info(f"Started collecting Exercise {exercise_match.group(1)} from page {page_num}")
                    
                elif example_match:
                    exercise_buffer = {
                        'text': page_text,
                        'number': example_match.group(1),
                        'start_page': page_num,
                        'type': 'example',
                        'images': []
                    }
                    # Init images with current page's images
                    exercise_buffer['images'].extend(current_page_images)
                    collecting_exercise = True
                    logger.info(f"Started collecting Example {example_match.group(1)} from page {page_num}")
            
            elif collecting_exercise:
                # Continue collecting until we hit another exercise/example or significant break
                # Check if we've hit a new major section
                if re.search(r'(MISCELLANEOUS|SUMMARY|CHAPTER)', page_text, re.IGNORECASE):
                    # Stop collecting and save
                    # Stop collecting and save
                    collection_chunks = self._create_collection_chunk(
                        exercise_buffer,
                        document_id,
                        class_level,
                        current_chapter,
                        current_section,
                        page_images=exercise_buffer['images'],
                        page_tables=current_page_tables
                    )
                    if collection_chunks:
                        chunks.extend(collection_chunks)
                    collecting_exercise = False
                else:
                    # Add to buffer
                    exercise_buffer['text'] += '\n\n' + page_text
                    
                     
                    # Also need to consider how to accrue images across pages for multi-page exercises
                    # Accumulate images in buffer
                    for img in current_page_images:
                        # Avoid duplicates
                        if not any(existing['image_id'] == img['image_id'] for existing in exercise_buffer['images']):
                            exercise_buffer['images'].append(img)
            
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
            collection_chunks = self._create_collection_chunk(
                exercise_buffer,
                document_id,
                class_level,
                current_chapter,
                current_section,
                page_images=exercise_buffer['images']
            )
            if collection_chunks:
                chunks.extend(collection_chunks)
        
        logger.info(f"Created {len(chunks)} chunks from document (with smart grouping)")
        return chunks
    
    def _link_content_to_chunk(
        self,
        chunk: ContentChunk,
        page_images: List[Dict[str, Any]],
        page_tables: List[Dict[str, Any]]
    ):
        """
        Smart linking of images and tables to chunk.
        
        Strategies:
        1. Reference Check: Does chunk text say "Fig 1.1"?
        2. Proximity Check: Is image/table spatially near the text?
        """
        if not (page_images or page_tables):
            return

        # 1. Reference Linking
        # Regex to find figure references like "Fig. 1.1", "Figure 1", "Table 2.3"
        fig_refs = re.findall(r'Fig(?:ure)?\.?\s*(\d+(?:\.\d+)?)', chunk.text_content, re.IGNORECASE)
        table_refs = re.findall(r'Table\s*(\d+(?:\.\d+)?)', chunk.text_content, re.IGNORECASE)
        
        # Link referenced images
        for fig_ref in fig_refs:
            # Normalize ref (e.g. "1.1")
            ref_id = fig_ref.replace('.', '_')
            for img in page_images:
                # Check if image ID contains this reference
                # We stored image_id as "fig_1_1"
                if f"fig_{ref_id}" in img['image_id']:
                    # Create ImageData object
                    img_obj = ImageData(
                        image_id=img['image_id'],
                        image_path=img['image_path'],
                        image_type=ImageType.DIAGRAM, # Assuming diagram for now
                        description=img.get('description', ''),
                        page_number=img['page_number'],
                        bbox=img.get('bbox')
                    )
                    # Avoid duplicates
                    if not any(i.image_id == img_obj.image_id for i in chunk.images):
                        chunk.images.append(img_obj)
                        logger.debug(f"Linked image {img['image_id']} to chunk {chunk.chunk_id} via reference")

        # Link referenced tables
        for tab_ref in table_refs:
            ref_id = tab_ref.replace('.', '_')
            for tbl in page_tables:
                # Check if table ID contains this reference
                # Table IDs are "table_pX_Y" - we might need to store table_num if we parse caption
                # For now, if we don't have table numbers in extraction, we look for matching ID
                if f"table_{ref_id}" in tbl['table_id']:
                    from utils.schema import TableData
                    tbl_obj = TableData(
                        table_id=tbl['table_id'],
                        table_path=tbl.get('table_path', ''),
                        markdown_content=tbl['markdown_content'],
                        csv_content=tbl.get('csv_content'),
                        num_rows=tbl['num_rows'],
                        num_cols=tbl['num_cols'],
                        has_header=tbl['has_header'],
                        page_number=tbl['page_number'],
                        bbox=tbl.get('bbox')
                    )
                    if not any(t.table_id == tbl_obj.table_id for t in chunk.tables):
                        chunk.tables.append(tbl_obj)
                        logger.debug(f"Linked table {tbl['table_id']} to chunk {chunk.chunk_id} via reference") 

        # 2. Proximity/Containment Linking (Spatial)
        # Only if we're on the same page
        
        # We need chunk's bbox? 
        # StructureAwareChunker currently aggregates text from blocks but doesn't track strict union bbox of all blocks.
        # However, for exercise/example chunks, we know they often span a specific range.
        
        # Simplified Proximity: 
        # If this chunk is the "primary" content of the page (e.g. large chunk), 
        # or if the image is "orphaned" (not linked by ref), assign to nearest chunk?
        
        # For now, let's rely heavily on Reference Linking as per user request ("if an only if... show it")
        # But user also said "if answer and image are under same heading"
        
        # Context Match:
        # If chunk is "Example 1", and image caption is "Fig 1.1: Diagram for Example 1", that's a match.
        
        pass

    def _create_collection_chunk(
        self,
        buffer: Dict[str, Any],
        document_id: str,
        class_level: str,
        chapter: Dict[str, Any],
        section: Dict[str, Any],
        page_images: List[Dict[str, Any]] = None,
        page_tables: List[Dict[str, Any]] = None
    ) -> List[ContentChunk]:
        """Create chunks from collected exercise/example content with smart splitting."""
        if not buffer['text'].strip():
            return []
        
        chunk_type = ContentType.EXERCISE if buffer['type'] == 'exercise' else ContentType.EXAMPLE
        
        # Calculate size limit (approx chars: tokens * 4)
        # Using factor 3.5 to be safe
        max_chars = self.max_tokens * 3.5
        
        text = buffer['text']
        total_len = len(text)
        
        # If small enough, create single chunk
        if total_len <= max_chars:
            equations = self.math_detector.extract_equations(text)
            chunk = ContentChunk(
                chunk_id=str(uuid.uuid4()),
                document_id=document_id,
                class_level=class_level,
                chapter_number=chapter.get('number', 0),
                chapter_name=chapter.get('name', ''),
                section_name=section.get('name', ''),
                content_type=chunk_type,
                text_content=text,
                page_number=buffer['start_page'],
                latex_equations=equations,
                images=[],
                tables=[],
                example_number=buffer['number'] if buffer['type'] == 'example' else None,
                exercise_number=buffer['number'] if buffer['type'] == 'exercise' else None
            )
            # Link images
            if page_images or page_tables:
                self._link_content_to_chunk(chunk, page_images or [], page_tables or [])
            return [chunk]
            
        # If too large, split by paragraphs
        logger.info(f"Splitting large collection chunk ({total_len} chars) for {buffer['type']} {buffer['number']}")
        
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk_text = ""
        part_num = 1
        
        for para in paragraphs:
            if not para.strip():
                continue
                
            if len(current_chunk_text) + len(para) > max_chars and current_chunk_text:
                # Finalize current chunk
                equations = self.math_detector.extract_equations(current_chunk_text)
                
                # Add context header for parts > 1 if missing
                final_text = current_chunk_text
                if part_num > 1 and f"{buffer['type']} {buffer['number']}".lower() not in final_text.lower()[:50]:
                    final_text = f"[{buffer['type'].capitalize()} {buffer['number']} (Part {part_num})]\n\n" + final_text
                
                chunk = ContentChunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    class_level=class_level,
                    chapter_number=chapter.get('number', 0),
                    chapter_name=chapter.get('name', ''),
                    section_name=section.get('name', ''),
                    content_type=chunk_type,
                    text_content=final_text,
                    page_number=buffer['start_page'], # Approximate page
                    latex_equations=equations,
                    images=[],
                    tables=[],
                    example_number=buffer['number'] if buffer['type'] == 'example' else None,
                    exercise_number=buffer['number'] if buffer['type'] == 'exercise' else None
                )
                
                # Link images - link ALL collected images to ALL parts for safety
                # (Smart linking inside _link_content_to_chunk will filter by ref if found, 
                # but we want to ensure availability)
                if page_images or page_tables:
                     self._link_content_to_chunk(chunk, page_images or [], page_tables or [])
                
                chunks.append(chunk)
                
                current_chunk_text = para
                part_num += 1
            else:
                current_chunk_text += '\n\n' + para if current_chunk_text else para
                
        # Final part
        if current_chunk_text.strip():
            equations = self.math_detector.extract_equations(current_chunk_text)
            final_text = current_chunk_text
            if part_num > 1 and f"{buffer['type']} {buffer['number']}".lower() not in final_text.lower()[:50]:
                final_text = f"[{buffer['type'].capitalize()} {buffer['number']} (Part {part_num})]\n\n" + final_text
            
            chunk = ContentChunk(
                chunk_id=str(uuid.uuid4()),
                document_id=document_id,
                class_level=class_level,
                chapter_number=chapter.get('number', 0),
                chapter_name=chapter.get('name', ''),
                section_name=section.get('name', ''),
                content_type=chunk_type,
                text_content=final_text,
                page_number=buffer['start_page'],
                latex_equations=equations,
                images=[],
                tables=[],
                example_number=buffer['number'] if buffer['type'] == 'example' else None,
                exercise_number=buffer['number'] if buffer['type'] == 'exercise' else None
            )
            if page_images or page_tables:
                 self._link_content_to_chunk(chunk, page_images or [], page_tables or [])
            chunks.append(chunk)

        # -------------------------------------------------------------------------
        # ORPHAN RESCUE STRATEGY
        # -------------------------------------------------------------------------
        # Check if any images in our collected buffer were NOT linked to any chunk.
        # This happens if the text didn't explicitly say "Fig X".
        
        if page_images:
            # 1. Gather all linked image IDs across all generated chunks
            linked_image_ids = set()
            for c in chunks:
                for img in c.images:
                    linked_image_ids.add(img.image_id)
            
            # 2. Find orphans
            orphans = [img for img in page_images if img['image_id'] not in linked_image_ids]
            
            if orphans:
                logger.info(f"Found {len(orphans)} orphaned images. Attempting rescue...")
                from utils.schema import ImageData, ImageType
                
                for orphan in orphans:
                    # 3. Rescue: Assign to chunks on the SAME PAGE
                    # If multiple chunks are on the same page, assign to the LAST one (usually where the exercise text is)
                    # or ALL of them? Let's assign to ALL chunks on that page to be safe.
                    orphan_page = orphan['page_number']
                    target_chunks = [c for c in chunks if c.page_number == orphan_page]
                    
                    if target_chunks:
                        # Create Image Object
                        img_obj = ImageData(
                            image_id=orphan['image_id'],
                            image_path=orphan['image_path'],
                            image_type=ImageType.DIAGRAM,
                            description=orphan.get('description', ''),
                            page_number=orphan['page_number'],
                            bbox=orphan.get('bbox')
                        )
                        
                        # Link to target chunks
                        for tc in target_chunks:
                            if not any(i.image_id == img_obj.image_id for i in tc.images):
                                tc.images.append(img_obj)
                                logger.debug(f"Rescue: Linked orphan {orphan['image_id']} to chunk {tc.chunk_id}")
                    else:
                        logger.warning(f"Could not rescue orphan {orphan['image_id']} (Page {orphan_page}) - no chunks on this page.")

        logger.info(f"Split collection into {len(chunks)} parts")
        return chunks
    
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
        
        # Access page-level images/tables if passed 
        # (Need to update signature or assume page dict has them)
        page_images = page.get('images', [])
        page_tables = page.get('tables', [])
        
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
                    if page_images or page_tables:
                        self._link_content_to_chunk(chunk, page_images, page_tables)
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
                if page_images or page_tables:
                    self._link_content_to_chunk(chunk, page_images, page_tables)
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
