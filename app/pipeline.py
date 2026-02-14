"""Main RAG pipeline orchestrator."""

from pathlib import Path
from typing import Dict, Any, Optional, List
from config import get_config, get_yaml_config
from utils.logging import LoggerSetup, get_logger
from utils.schema import ContentChunk
from extraction.pdf_extractor import PDFExtractor
from extraction.ocr_processor import OCRProcessor, ImageDescriptionGenerator
from extraction.content_parser import ContentParser
from chunking.structure_aware_chunker import StructureAwareChunker
from embeddings.embedding_generator import EmbeddingGenerator
from storage.vector_store import FAISSVectorStore
from storage.metadata_store import MetadataStore
from llm.groq_client import GroqClient
from retrieval.hybrid_retriever import HybridRetriever, QueryClassifier, RetrievalPipeline
import numpy as np

logger = get_logger(__name__)


class MathRAGPipeline:
    """Complete RAG pipeline for mathematics textbooks."""
    
    def __init__(self):
        """Initialize RAG pipeline."""
        logger.info("Initializing Math RAG Pipeline...")
        
        # Load configuration
        self.config = get_config()
        
        # Setup logging
        LoggerSetup.setup(
            log_file=self.config.log_file,
            log_level=self.config.log_level
        )
        
        # Initialize components (lazy loading)
        self._pdf_config = get_yaml_config('pdf_processing')
        self._chunking_config = get_yaml_config('chunking')
        self._embedding_config = get_yaml_config('embeddings')
        self._llm_config = get_yaml_config('llm')
        self._retrieval_config = get_yaml_config('retrieval')
        
        # Components
        self.ocr_processor: Optional[OCRProcessor] = None
        self.image_describer: Optional[ImageDescriptionGenerator] = None
        self.content_parser: Optional[ContentParser] = None
        self.chunker: Optional[StructureAwareChunker] = None
        self.embedding_generator: Optional[EmbeddingGenerator] = None
        self.vector_store: Optional[FAISSVectorStore] = None
        self.metadata_store: Optional[MetadataStore] = None
        self.llm_client: Optional[GroqClient] = None
        self.retriever: Optional[HybridRetriever] = None
        self.retrieval_pipeline: Optional[RetrievalPipeline] = None
        
        logger.info("Pipeline initialized")
    
    def index_document(
        self,
        pdf_path: str,
        class_level: str,
        force_reindex: bool = False
    ) -> Dict[str, Any]:
        """
        Index a PDF document.
        
        Args:
            pdf_path: Path to PDF file
            class_level: Class level (11 or 12)
            force_reindex: Force reindexing even if exists
            
        Returns:
            Indexing statistics
        """
        logger.info(f"Starting indexing for: {pdf_path}")
        
        pdf_path = Path(pdf_path)
        document_id = pdf_path.stem
        
        # Initialize components
        self._init_indexing_components()
        
        # Step 1: Extract PDF content
        logger.info("Step 1: Extracting PDF content...")
        extractor = PDFExtractor(str(pdf_path), str(self.config.processed_dir))
        extraction_result = extractor.extract_all()
        
        # Step 2: Process images and tables
        logger.info("Step 2: Processing visual content...")
        self._process_images(extraction_result['images'])
        self._process_tables(extraction_result['tables'])
        
        # Step 3: Parse content structure
        logger.info("Step 3: Parsing document structure...")
        structured_content = self.content_parser.parse_document_structure(
            extraction_result['pages']
        )
        
        # Step 4: Create chunks
        logger.info("Step 4: Creating structured chunks...")
        chunks = self.chunker.chunk_document(
            extraction_result['pages'],
            document_id,
            class_level
        )
        
        if not chunks:
            logger.warning("No chunks created from document. Checking extraction results...")
            logger.info(f"Extracted pages: {len(extraction_result['pages'])}")
            if extraction_result['pages']:
                logger.info(f"First page text length: {len(extraction_result['pages'][0]['text'])}")
                logger.debug(f"First page text preview: {extraction_result['pages'][0]['text'][:200]}")
            
            return {
                'document_id': document_id,
                'class_level': class_level,
                'total_pages': extraction_result['total_pages'],
                'total_chunks': 0,
                'total_images': len(extraction_result['images']),
                'total_tables': len(extraction_result['tables']),
                'total_embeddings': 0
            }

        # Step 5: Generate embeddings
        logger.info("Step 5: Generating embeddings...")
        embeddings_dict = self.embedding_generator.embed_chunks(chunks)
        
        # Step 6: Store in vector store
        logger.info("Step 6: Storing in vector database...")
        chunk_ids = list(embeddings_dict.keys())
        embeddings_array = np.array([embeddings_dict[cid] for cid in chunk_ids])
        self.vector_store.add_embeddings(embeddings_array, chunk_ids)
        
        # Step 7: Store metadata
        logger.info("Step 7: Storing metadata...")
        self.metadata_store.add_chunks(chunks)
        
        # Step 8: Build Keyword Index (BM25)
        logger.info("Step 8: Updating Keyword Index (BM25)...")
        # We need to initialize the retriever component to access the keyword retriever
        # OR just instantiate a temporary one if we don't want to load the whole retrieval pipeline
        from retrieval.keyword_retriever import KeywordRetriever
        
        # Merge config
        retrieval_config = self._retrieval_config.copy()
        
        # Initialize and index
        kw_retriever = KeywordRetriever(retrieval_config)
        # We need to index ALL chunks, not just the new ones, because BM25 is usually global.
        # However, for simplicity/MVP, let's just re-index everything in the metadata store + new chunks?
        # Ideally, we should fetch all chunks from metadata store.
        all_chunks = self.metadata_store.filter_chunks() # Get everything
        kw_retriever.index_chunks(all_chunks)
        
        # Save
        self._save_stores()
        
        # Generate stats
        stats = {
            'document_id': document_id,
            'class_level': class_level,
            'total_pages': extraction_result['total_pages'],
            'total_chunks': len(chunks),
            'total_images': len(extraction_result['images']),
            'total_tables': len(extraction_result['tables']),
            'total_embeddings': len(embeddings_dict)
        }
        
        logger.info(f"Indexing complete: {stats}")
        return stats
    
    def query(
        self,
        query: str,
        class_level: Optional[str] = None,
        chapter_number: Optional[int] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            query: User query
            class_level: Optional class filter
            chapter_number: Optional chapter filter
            top_k: Number of results
            
        Returns:
            Query response with answer and sources
        """
        logger.info(f"Processing query: {query}")
        
        # Initialize components
        self._init_query_components()
        
        # Retrieve relevant chunks
        results = self.retrieval_pipeline.search(
            query=query,
            top_k=top_k,
            class_level=class_level,
            chapter_number=chapter_number
        )
        
        if not results:
            return {
                'answer': "I couldn't find relevant information in the textbook to answer your question.",
                'sources': [],
                'confidence': 0.0
            }
        
        # Smart Filter: Only keep images from HIGH relevance chunks
        # This prevents images from "semi-relevant" chunks (rank 4-5) from polluting context/UI
        best_score = results[0].score
        score_threshold = best_score * 0.9  # strict 90% threshold relative to best match
        
        # Filter for LLM Context
        context_chunks = self.retrieval_pipeline.format_results_for_llm(results)
        for i, chunk_ctx in enumerate(context_chunks):
            # If score is too low compared to best, remove image descriptions
            # We map index i back to results[i] since list order is preserved
            if results[i].score < score_threshold:
                if 'images' in chunk_ctx:
                    del chunk_ctx['images']
        
        # Generate answer
        logger.info("Generating answer...")
        llm_response = self.llm_client.generate_with_context(query, context_chunks)
        answer = llm_response['content']
        
        # Post-process answer to ensure clean formatting
        answer = self._post_process_answer(answer)
        
        # Prepare response
        source_list = []
        for r in results:
            src_data = {
                'chunk_id': r.chunk.chunk_id,
                'chapter': f"Chapter {r.chunk.chapter_number}: {r.chunk.chapter_name}",
                'section': r.chunk.section_name,
                'content_type': r.chunk.content_type.value,
                'page': r.chunk.page_number,
                'score': r.score,
                'text_preview': r.chunk.text_content[:200] + "...",
                'images': [], # Default empty
                'tables': [tbl.table_path for tbl in r.chunk.tables]
            }
            
            # Only include images in UI if score is high enough
            if r.score >= score_threshold:
                src_data['images'] = [img.image_path for img in r.chunk.images]
            
            source_list.append(src_data)

        response = {
            'answer': answer,
            'model': llm_response.get('model'),
            'usage': llm_response.get('usage'),
            'sources': source_list,
            'confidence': results[0].score if results else 0.0
        }
        
        return response
    
    def _init_indexing_components(self):
        """Initialize components needed for indexing."""
        if not self.ocr_processor:
            self.ocr_processor = OCRProcessor()
        
        if not self.image_describer:
            self.image_describer = ImageDescriptionGenerator()
        
        if not self.content_parser:
            self.content_parser = ContentParser(self.config.yaml_config)
        
        if not self.chunker:
            self.chunker = StructureAwareChunker(self._chunking_config)
        
        if not self.embedding_generator:
            self.embedding_generator = EmbeddingGenerator(
                model_name=self.config.embedding_model,
                device=self._embedding_config.get('device', 'cpu')
            )
        
        if not self.vector_store:
            self.vector_store = FAISSVectorStore(
                dimension=self.config.embedding_dimension,
                index_type=get_yaml_config('vector_store').get('index_type', 'IndexFlatIP')
            )
        
        if not self.metadata_store:
            self.metadata_store = MetadataStore(self.config.metadata_db_path)
    
    def _init_query_components(self):
        """Initialize components needed for querying."""
        # Load vector store and metadata if not loaded
        if not self.vector_store:
            if self.config.vector_db_path.exists():
                self.vector_store = FAISSVectorStore.load(self.config.vector_db_path)
            else:
                raise ValueError("Vector store not found. Please index documents first.")
        
        if not self.metadata_store:
            self.metadata_store = MetadataStore(self.config.metadata_db_path)
        
        if not self.embedding_generator:
            self.embedding_generator = EmbeddingGenerator(
                model_name=self.config.embedding_model,
                device=self._embedding_config.get('device', 'cpu')
            )
        
        if not self.llm_client:
            if not self.config.groq_api_key:
                raise ValueError("Groq API key not found in configuration")
            
            self.llm_client = GroqClient(
                api_key=self.config.groq_api_key,
                model=self.config.groq_model,
                temperature=self._llm_config.get('temperature', 0.1),
                max_tokens=self._llm_config.get('max_tokens', 2048)
            )
        
        if not self.retriever:
            # Merge system config into retrieval config
            retrieval_config = self._retrieval_config.copy()
            retrieval_config['similarity_threshold'] = self.config.similarity_threshold
            
            self.retriever = HybridRetriever(
                vector_store=self.vector_store,
                metadata_store=self.metadata_store,
                embedding_generator=self.embedding_generator,
                config=retrieval_config
            )

        # Build/Update BM25 Index if needed (lazy load is handled in init, but we might want to refresh)
        # For now, let's assume it loads from disk or is built during indexing.

        
        if not self.retrieval_pipeline:
            self.retrieval_pipeline = RetrievalPipeline(
                retriever=self.retriever,
                classifier=QueryClassifier()
            )
    
    def _process_images(self, images: List[Dict[str, Any]]):
        """Process images with OCR and description."""
        for image in images:
            img_path = image.get('image_path')
            if not img_path:
                continue
                
            # Check if contains text
            if self.ocr_processor.contains_text(img_path):
                image['contains_text'] = True
                image['ocr_text'] = self.ocr_processor.extract_text(img_path)
            
            # Generate description
            img_type = image.get('image_type', 'diagram')
            image['description'] = self.image_describer.generate_description(
                img_path,
                img_type
            )
            
    def _process_tables(self, tables: List[Dict[str, Any]]):
        """Placeholder for table processing (e.g. OCR if math heavy)."""
        # Tables extracted via find_tables already have markdown_content
        pass

    def _post_process_answer(self, text: str) -> str:
        """
        Clean up LLM response formatting while protecting LaTeX and structural blocks.
        """
        import re
        
        # 0. Placeholder-based protection for LaTeX
        latex_placeholders = {}
        
        def protect_latex(match):
            placeholder = f"__LATEX_PH_{len(latex_placeholders)}__"
            latex_placeholders[placeholder] = match.group(0)
            return placeholder

        # Protect block math $$...$$
        text = re.sub(r'\$\$.*?\$\$', protect_latex, text, flags=re.DOTALL)
        # Protect inline math $...$
        text = re.sub(r'\$.*?\$', protect_latex, text)
        
        # 1. Clean up potential weird artifacts
        text = text.replace('— -', '\n\n')
        
        # 2. Force newlines before Headers (### or ####)
        text = re.sub(r'\s*(#{3,4})\s*', r'\n\n\1 ', text)
        
        # 3. Force newlines before Bullet Points (* or -) IF NOT inside a blockquote
        # We avoid matching if preceded by '>' (part of blockquote)
        text = re.sub(r'([^>\n])\s*([\*\-])\s+', r'\1\n\2 ', text)
        
        # 4. Force newlines before Numbered Lists (1., 2., etc.) IF NOT inside a blockquote
        text = re.sub(r'([^>\n])\s+(\d+\.\s)', r'\1\n\2', text)
        
        # 5. Fix "Step X:" patterns that might be inline
        text = re.sub(r'([^>\n])\s*(Step \d+:)', r'\1\n\n**\2**', text)
        
        # 6. Clean up excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 7. Restore LaTeX and ensure block math has newlines
        for placeholder, original in latex_placeholders.items():
            if original.startswith('$$'):
                # Ensure block math is on its own line
                replacement = f"\n\n{original}\n\n"
                text = text.replace(placeholder, replacement)
            else:
                text = text.replace(placeholder, original)
        
        # 8. Final check: Ensure blockquotes are properly formatted if they were broken
        # (Though the [^>] above should prevent most issues)
        
        # Final cleanup of excessive newlines after restoration
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _save_stores(self):
        """Save vector store and metadata."""
        logger.info("Saving vector store and metadata...")
        self.vector_store.save(self.config.vector_db_path)
        self.metadata_store.save()
        logger.info("Stores saved successfully")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        if not self.metadata_store:
            self.metadata_store = MetadataStore(self.config.metadata_db_path)
        
        if not self.vector_store and self.config.vector_db_path.exists():
            self.vector_store = FAISSVectorStore.load(self.config.vector_db_path)
        
        stats = {
            'metadata': self.metadata_store.get_stats() if self.metadata_store else {},
            'vector_store': self.vector_store.get_stats() if self.vector_store else {}
        }
        
        return stats

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all available documents.
        
        Returns:
            List of document summaries
        """
        if not self.metadata_store:
            self.metadata_store = MetadataStore(self.config.metadata_db_path)
        return self.metadata_store.list_documents()

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and its embeddings.
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            Success status
        """
        logger.info(f"Deleting document: {document_id}")
        
        # Initialize stores if needed
        if not self.metadata_store:
            self.metadata_store = MetadataStore(self.config.metadata_db_path)
        
        if not self.vector_store and self.config.vector_db_path.exists():
            self.vector_store = FAISSVectorStore.load(self.config.vector_db_path)
        elif not self.vector_store:
            logger.warning("Vector store not initialized, cannot delete embeddings")
            return False

        # 1. Delete from metadata store and get chunk IDs
        deleted_chunk_ids = self.metadata_store.delete_document(document_id)
        
        if not deleted_chunk_ids:
            logger.warning(f"No chunks found for document: {document_id}")
            return False
            
        # 2. Delete from vector store
        self.vector_store.remove_by_ids(deleted_chunk_ids)
        
        # 3. Save changes
        self._save_stores()
        
        logger.info(f"Successfully deleted document {document_id}")
        return True