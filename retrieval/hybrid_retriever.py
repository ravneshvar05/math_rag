"""Retrieval system for finding relevant chunks."""

from typing import List, Dict, Any, Optional
import numpy as np
import re
from utils.schema import ContentChunk, RetrievalResult
from storage.vector_store import FAISSVectorStore
from storage.metadata_store import MetadataStore
from embeddings.embedding_generator import EmbeddingGenerator
from utils.logging import get_logger

logger = get_logger(__name__)


from retrieval.keyword_retriever import KeywordRetriever

class HybridRetriever:
    """Hybrid retrieval combining vector search, keyword search, and metadata filtering."""
    
    def __init__(
        self,
        vector_store: FAISSVectorStore,
        metadata_store: MetadataStore,
        embedding_generator: EmbeddingGenerator,
        config: Dict[str, Any]
    ):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_store: FAISS vector store
            metadata_store: Metadata store
            embedding_generator: Embedding generator
            config: Retrieval configuration
        """
        self.vector_store = vector_store
        self.metadata_store = metadata_store
        self.embedding_generator = embedding_generator
        self.config = config
        
        self.keyword_retriever = KeywordRetriever(config)
        
        self.top_k = config.get('top_k', 5)
        self.similarity_threshold = config.get('similarity_threshold', 0.7)
        self.alpha = config.get('alpha', 0.7) # Vector weight (0.0 to 1.0)
        
        logger.info("Initialized hybrid retriever (Vector + Keyword)")
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks using Hybrid Search (Vector + Keyword).
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Metadata filters to apply
            
        Returns:
            List of retrieval results
        """
        k = top_k or self.top_k
        logger.info(f"Hybrid retrieving top {k} results for query: {query[:50]}...")
        
        # 1. Dynamic Weighting Logic
        # Default to configured alpha (usually 0.7 favoring vector)
        current_alpha = self.alpha
        
        # Check if query is "Entity-Heavy" (specific lookup)
        is_entity_query = self._is_entity_query(query)
        if is_entity_query:
            logger.info("Detected Entity Query (Example/Exercise) -> Boosting Keyword Search")
            current_alpha = 0.3 # Favor Keyword (0.3 Vector, 0.7 Keyword)
            
        # 1. Vector Search
        query_embedding = self.embedding_generator.generate_embedding(query)
        if filters:
            filtered_chunks = self.metadata_store.filter_chunks(**filters)
            filtered_ids = [chunk['chunk_id'] for chunk in filtered_chunks]
            vector_results = self.vector_store.search_with_filter(query_embedding, k * 2, filtered_ids)
        else:
            vector_results = self.vector_store.search(query_embedding, k * 2)
            
        # 2. Keyword Search
        keyword_results = self.keyword_retriever.search(query, top_k=k * 2)
        
        # 3. Fuse Scores
        fused_scores = {}
        
        # Helper for RRF
        def apply_rrf(results, rank_constant=60, weight=1.0):
            for rank, (chunk_id, _) in enumerate(results):
                if filters:
                    # Double check filter for keyword results
                    chunk = self.metadata_store.get_chunk(chunk_id)
                    if not chunk: continue
                    match = True
                    for key, val in filters.items():
                        if chunk.get(key) != val:
                            match = False
                            break
                    if not match: continue
                
                if chunk_id not in fused_scores:
                    fused_scores[chunk_id] = 0.0
                fused_scores[chunk_id] += weight * (1 / (rank_constant + rank + 1))

        apply_rrf(vector_results, weight=current_alpha)
        apply_rrf(keyword_results, weight=(1.0 - current_alpha))
        
        # Sort by fused score
        sorted_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        # Get chunks and create retrieval results
        retrieval_results = []
        for rank, (chunk_id, score) in enumerate(sorted_results, 1):
            chunk_data = self.metadata_store.get_chunk(chunk_id)
            if chunk_data:
                try:
                    chunk = ContentChunk.from_dict(chunk_data)
                    retrieval_results.append(RetrievalResult(
                        chunk=chunk,
                        score=score,
                        rank=rank
                    ))
                except Exception as e:
                    logger.error(f"Error converting chunk {chunk_id}: {e}")
        
        logger.info(f"Retrieved {len(retrieval_results)} hybrid results")
        return retrieval_results
    
    def retrieve_by_type(
        self,
        query: str,
        content_type: str,
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve chunks of specific content type.
        
        Args:
            query: Search query
            content_type: Content type to filter
            top_k: Number of results
            
        Returns:
            Filtered retrieval results
        """
        return self.retrieve(
            query=query,
            top_k=top_k,
            filters={'content_type': content_type}
        )

    def _is_entity_query(self, query: str) -> bool:
        """
        Check if query is asking for a specific entity (Example X, Exercise Y).
        """
        import re
        # patterns for "Example 5", "Ex 5.1", "Exercise 3.2", "Q 1"
        patterns = [
            r'example\s*\d+',
            r'ex\s*\d+',
            r'exercise\s*\d+',
            r'question\s*\d+',
            r'q\s*\d+',
            r'problem\s*\d+'
        ]
        
        for pattern in patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
    
    def retrieve_from_chapter(
        self,
        query: str,
        class_level: str,
        chapter_number: int,
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve chunks from specific chapter.
        
        Args:
            query: Search query
            class_level: Class level
            chapter_number: Chapter number
            top_k: Number of results
            
        Returns:
            Chapter-filtered results
        """
        return self.retrieve(
            query=query,
            top_k=top_k,
            filters={
                'class_level': class_level,
                'chapter_number': chapter_number
            }
        )
    
    def get_related_chunks(
        self,
        chunk_id: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Get chunks related to a given chunk.
        
        Args:
            chunk_id: Reference chunk ID
            top_k: Number of related chunks
            
        Returns:
            Related chunks
        """
        # Get reference chunk
        ref_chunk = self.metadata_store.get_chunk(chunk_id)
        if not ref_chunk:
            return []
        
        # Use chunk's text as query
        query = ref_chunk.text_content[:500]  # First 500 chars
        
        # Retrieve
        results = self.retrieve(query, top_k=top_k + 1)
        
        # Filter out the reference chunk itself
        results = [r for r in results if r.chunk.chunk_id != chunk_id]
        
        return results[:top_k]

    def retrieve_by_example(
        self,
        query: str,
        example_number: str,
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve specific example.
        
        Args:
            query: Search query
            example_number: Example number to find
            top_k: Number of results
            
        Returns:
            Example results
        """
        return self.retrieve(
            query=query,
            top_k=top_k,
            filters={'example_number': example_number}
        )

class QueryClassifier:
    """Classify queries to determine search strategy."""
    
    def __init__(self):
        """Initialize query classifier."""
        self.query_types = {
            'definition': ['what is', 'define', 'meaning of', 'definition'],
            'theorem': ['theorem', 'prove', 'proof'],
            'formula': ['formula', 'equation', 'expression'],
            'example': ['example', 'demonstrate', 'illustrate'],
            'exercise': ['solve', 'exercise', 'problem', 'question'],
            'concept': ['explain', 'how', 'why', 'concept']
        }
    
    def classify(self, query: str) -> str:
        """
        Classify query type.
        
        Args:
            query: User query
            
        Returns:
            Query type
        """
        query_lower = query.lower()
        
        # specific check for example numbers
        if self.extract_example_number(query):
            return 'example'
            
        for query_type, keywords in self.query_types.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return query_type
        
        return 'concept'  # Default
    
    def extract_example_range(self, query: str) -> Optional[List[str]]:
        """Extract a range of example numbers from query."""
        # Pattern for "example 2 to 5" or "examples 2-5"
        pattern = r'examples?\s+(\d+)\s*(?:to|-)\s*(\d+)'
        match = re.search(pattern, query, re.IGNORECASE)
        
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            
            # Sanity check: prevent huge ranges
            if end < start:
                start, end = end, start
            
            if end - start > 10:  # Limit to 10 examples max
                end = start + 10
                
            return [str(i) for i in range(start, end + 1)]
            
        return None

    def extract_example_number(self, query: str) -> Optional[str]:
        """Extract example number from query."""
        patterns = [
            r'example\s+(\d+(?:\.\d+)?)',
            r'ex\.\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

class RetrievalPipeline:
    """Complete retrieval pipeline with query processing."""
    
    def __init__(
        self,
        retriever: HybridRetriever,
        classifier: Optional[QueryClassifier] = None
    ):
        """
        Initialize retrieval pipeline.
        
        Args:
            retriever: Hybrid retriever
            classifier: Query classifier
        """
        self.retriever = retriever
        self.classifier = classifier or QueryClassifier()
        
        logger.info("Initialized retrieval pipeline")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        class_level: Optional[str] = None,
        chapter_number: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Complete search pipeline.
        
        Args:
            query: User query
            top_k: Number of results
            class_level: Optional class filter
            chapter_number: Optional chapter filter
            
        Returns:
            Retrieval results
        """
        logger.info(f"Processing query: {query}")
        
        # Classify query
        query_type = self.classifier.classify(query)
        logger.info(f"Query type: {query_type}")
        
        # Build filters
        filters = {}
        if class_level:
            filters['class_level'] = class_level
        if chapter_number:
            filters['chapter_number'] = chapter_number
        
        # Handle specific example queries
        if query_type == 'example':
            # Check for range first
            ex_range = self.classifier.extract_example_range(query)
            if ex_range:
                logger.info(f"Searching for Example range: {ex_range}")
                results = []
                for ex_num in ex_range:
                    ex_results = self.retriever.retrieve_by_example(
                        query=query,
                        example_number=ex_num,
                        top_k=2  # Fewer results per example in a range
                    )
                    results.extend(ex_results)
                
                if results:
                    return results[:top_k] # Limit total results

            # Fallback to single example
            ex_num = self.classifier.extract_example_number(query)
            if ex_num:
                logger.info(f"Searching for Example {ex_num}")
                results = self.retriever.retrieve_by_example(
                    query=query,
                    example_number=ex_num,
                    top_k=top_k
                )
                if results:
                    return results
                
                # If specific example not found in metadata, simple generic search is often better 
                # than 'retrieve_by_type' which might return wrong examples.
                # However, let's allow it to fall through but prioritize general search if we had a specific target number.
                logger.info(f"Example {ex_num} not found via strict metadata. Falling back to general search.")
                return self.retriever.retrieve(
                    query=query,
                    top_k=top_k,
                    filters=filters if filters else None
                )
        
        # Retrieve based on type
        if query_type in ['definition', 'theorem', 'formula', 'example']:
            # Search specifically for that type first
            results = self.retriever.retrieve_by_type(
                query=query,
                content_type=query_type,
                top_k=top_k
            )
            
            # If not enough results, do general search
            if len(results) < top_k // 2:
                general_results = self.retriever.retrieve(
                    query=query,
                    top_k=top_k,
                    filters=filters if filters else None
                )
                
                # Merge results, avoiding duplicates
                existing_ids = {r.chunk.chunk_id for r in results}
                for r in general_results:
                    if r.chunk.chunk_id not in existing_ids:
                        results.append(r)
                        if len(results) >= top_k:
                            break
        else:
            # General retrieval
            results = self.retriever.retrieve(
                query=query,
                top_k=top_k,
                filters=filters if filters else None
            )
        
        return results
    
    def format_results_for_llm(self, results: List[RetrievalResult]) -> List[Dict[str, Any]]:
        """
        Format retrieval results for LLM context.
        
        Args:
            results: Retrieval results
            
        Returns:
            Formatted context chunks
        """
        formatted = []
        
        for result in results:
            chunk = result.chunk
            
            # Basic info
            chunk_dict = {
                'text_content': chunk.text_content,
                'class_level': chunk.class_level,
                'chapter_number': chunk.chapter_number,
                'chapter_name': chunk.chapter_name,
                'section_name': chunk.section_name,
                'content_type': chunk.content_type.value,
                'score': result.score
            }
            
            # Add equations
            if chunk.latex_equations:
                chunk_dict['equations'] = [eq.latex for eq in chunk.latex_equations]
            
            # Add images
            if chunk.images:
                chunk_dict['images'] = [
                    {
                        'description': img.description,
                        'path': img.image_path,
                        'ocr_text': img.ocr_text
                    }
                    for img in chunk.images
                ]
            
            # Add tables
            if chunk.tables:
                chunk_dict['tables'] = [
                    {
                        'content': tbl.markdown_content,
                        'path': tbl.table_path
                    }
                    for tbl in chunk.tables
                ]
            
            formatted.append(chunk_dict)
        
        return formatted