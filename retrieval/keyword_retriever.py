
import logging
import pickle
from typing import List, Dict, Any, Tuple
from pathlib import Path
from rank_bm25 import BM25Okapi
import numpy as np
from utils.logging import get_logger

logger = get_logger(__name__)

class KeywordRetriever:
    """Keyword-based retriever using BM25."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize KeywordRetriever.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.bm25_path = Path(config.get('bm25_index_path', 'data/vector_store/bm25.pkl'))
        self.bm25 = None
        self.chunk_ids = []  # Map index to chunk_id
        
        # Load existing index if available
        if self.bm25_path.exists():
            self.load_index()

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Build BM25 index from chunks.
        
        Args:
            chunks: List of chunk dictionaries containing 'text_content' and 'chunk_id'
        """
        logger.info(f"Building BM25 index for {len(chunks)} chunks...")
        
        tokenized_corpus = [self._tokenize(chunk['text_content']) for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.chunk_ids = [chunk['chunk_id'] for chunk in chunks]
        
        self.save_index()
        logger.info("BM25 index built and saved.")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for documents matching query keywords.
        
        Args:
            query: User query string
            top_k: Number of results to return
            
        Returns:
            List of (chunk_id, score) tuples
        """
        if not self.bm25:
            logger.warning("BM25 index not initialized. Returning empty results.")
            return []
            
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_n = min(top_k, len(scores))
        if top_n == 0:
            return []
            
        top_indices = np.argsort(scores)[-top_n:][::-1]
        
        results = []
        for idx in top_indices:
            score = scores[idx]
            if score > 0: # Only return relevant results
                results.append((self.chunk_ids[idx], float(score)))
                
        return results

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer (lowercase split)."""
        return text.lower().split()

    def save_index(self):
        """Save BM25 index to disk."""
        self.bm25_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.bm25_path, 'wb') as f:
            pickle.dump({'bm25': self.bm25, 'chunk_ids': self.chunk_ids}, f)

    def load_index(self):
        """Load BM25 index from disk."""
        try:
            with open(self.bm25_path, 'rb') as f:
                data = pickle.load(f)
                self.bm25 = data['bm25']
                self.chunk_ids = data['chunk_ids']
            logger.info("BM25 index loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load BM25 index: {e}")
