"""FAISS vector store for similarity search."""
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import pickle
from utils.logging import get_logger

logger = get_logger(__name__)


class FAISSVectorStore:
    """FAISS-based vector store for embeddings."""
    
    def __init__(self, dimension: int, index_type: str = "IndexFlatIP"):
        """
        Initialize FAISS vector store.
        
        Args:
            dimension: Embedding dimension
            index_type: Type of FAISS index ('IndexFlatIP' for cosine similarity)
        """
        self.dimension = dimension
        self.index_type = index_type
        
        # Create index
        if index_type == "IndexFlatIP":
            # Inner product for normalized vectors (cosine similarity)
            self.index = faiss.IndexFlatIP(dimension)
        elif index_type == "IndexFlatL2":
            # L2 distance
            self.index = faiss.IndexFlatL2(dimension)
        else:
            # Default to flat IP
            self.index = faiss.IndexFlatIP(dimension)
        
        # Mapping from FAISS index to chunk_id
        self.id_map = []  # List of chunk_ids in order
        
        logger.info(f"Initialized FAISS index: {index_type}, dimension: {dimension}")
    
    def add_embeddings(
        self,
        embeddings: np.ndarray,
        chunk_ids: List[str]
    ):
        """
        Add embeddings to the index.
        
        Args:
            embeddings: Array of embeddings (n_samples, dimension)
            chunk_ids: List of chunk IDs corresponding to embeddings
        """
        if len(embeddings) != len(chunk_ids):
            raise ValueError("Number of embeddings must match number of chunk IDs")
        
        # Ensure embeddings are float32
        embeddings = embeddings.astype('float32')
        
        # Normalize if using inner product
        if self.index_type == "IndexFlatIP":
            faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Update ID mapping
        self.id_map.extend(chunk_ids)
        
        logger.info(f"Added {len(embeddings)} embeddings to index. Total: {self.index.ntotal}")
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (chunk_id, similarity_score) tuples
        """
        # Ensure query is float32 and 2D
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        # Normalize if using inner product
        if self.index_type == "IndexFlatIP":
            faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Convert to list of tuples
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.id_map):  # Valid index
                chunk_id = self.id_map[idx]
                results.append((chunk_id, float(score)))
        
        return results
    
    def search_with_filter(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        filter_chunk_ids: List[str]
    ) -> List[Tuple[str, float]]:
        """
        Search with filtering by chunk IDs.
        
        Args:
            query_embedding: Query embedding
            top_k: Number of results
            filter_chunk_ids: List of allowed chunk IDs
            
        Returns:
            Filtered search results
        """
        # Get more results initially
        initial_k = min(top_k * 10, self.index.ntotal)
        all_results = self.search(query_embedding, initial_k)
        
        # Filter results
        filtered_results = [
            (chunk_id, score)
            for chunk_id, score in all_results
            if chunk_id in filter_chunk_ids
        ]
        
        return filtered_results[:top_k]
    
    def save(self, save_path: Path):
        """
        Save index to disk.
        
        Args:
            save_path: Path to save directory
        """
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_file = save_path / "index.faiss"
        faiss.write_index(self.index, str(index_file))
        
        # Save ID mapping
        id_map_file = save_path / "id_map.pkl"
        with open(id_map_file, 'wb') as f:
            pickle.dump(self.id_map, f)
        
        # Save metadata
        metadata_file = save_path / "metadata.pkl"
        metadata = {
            'dimension': self.dimension,
            'index_type': self.index_type,
            'num_vectors': self.index.ntotal
        }
        with open(metadata_file, 'wb') as f:
            pickle.dump(metadata, f)
        
        logger.info(f"Saved vector store to {save_path}")
    
    @classmethod
    def load(cls, load_path: Path) -> 'FAISSVectorStore':
        """
        Load index from disk.
        
        Args:
            load_path: Path to load directory
            
        Returns:
            Loaded FAISSVectorStore instance
        """
        load_path = Path(load_path)
        
        # Load metadata
        metadata_file = load_path / "metadata.pkl"
        with open(metadata_file, 'rb') as f:
            metadata = pickle.load(f)
        
        # Create instance
        store = cls(
            dimension=metadata['dimension'],
            index_type=metadata['index_type']
        )
        
        # Load FAISS index
        index_file = load_path / "index.faiss"
        store.index = faiss.read_index(str(index_file))
        
        # Load ID mapping
        id_map_file = load_path / "id_map.pkl"
        with open(id_map_file, 'rb') as f:
            store.id_map = pickle.load(f)
        
        logger.info(f"Loaded vector store from {load_path}")
        logger.info(f"Total vectors: {store.index.ntotal}")
        
        return store
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'id_map_size': len(self.id_map)
        }
    
    def remove_by_ids(self, chunk_ids: List[str]):
        """
        Remove vectors by chunk IDs (requires rebuilding index).
        
        Args:
            chunk_ids: List of chunk IDs to remove
        """
        # Get indices to keep
        keep_indices = [
            i for i, chunk_id in enumerate(self.id_map)
            if chunk_id not in chunk_ids
        ]
        
        if len(keep_indices) == len(self.id_map):
            logger.info("No vectors to remove")
            return
        
        # Rebuild index with kept vectors
        logger.info(f"Removing {len(self.id_map) - len(keep_indices)} vectors")
        
        if not keep_indices:
            self.index.reset()
            self.id_map = []
            logger.info("Removed all vectors. Index is now empty.")
            return

        # Extract kept vectors
        kept_vectors = np.array([
            self.index.reconstruct(i) for i in keep_indices
        ])
        
        # Rebuild index
        self.index.reset()
        self.index.add(kept_vectors.astype('float32'))
        
        # Update ID map
        self.id_map = [self.id_map[i] for i in keep_indices]
        
        logger.info(f"Rebuilt index with {self.index.ntotal} vectors")

