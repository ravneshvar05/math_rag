"""Embedding generation using sentence transformers."""

import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import torch
from utils.schema import ContentChunk
from utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for content chunks."""
    
    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5", device: str = "cpu"):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Name of sentence transformer model
            device: Device to run on ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device
        
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def generate_embedding(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding for single text.
        
        Args:
            text: Input text
            normalize: Whether to normalize embedding
            
        Returns:
            Embedding vector
        """
        if not text or not text.strip():
            return np.zeros(self.dimension)
        
        embedding = self.model.encode(
            text,
            normalize_embeddings=normalize,
            show_progress_bar=False
        )
        
        return embedding
    
    def generate_batch_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for batch of texts.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            normalize: Whether to normalize embeddings
            
        Returns:
            Array of embeddings
        """
        if not texts:
            return np.array([])
        
        logger.info(f"Generating embeddings for {len(texts)} texts")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=normalize,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def embed_chunks(
        self,
        chunks: List[ContentChunk],
        batch_size: int = 32
    ) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for content chunks.
        
        Args:
            chunks: List of content chunks
            batch_size: Batch size for processing
            
        Returns:
            Dictionary mapping chunk_id to embedding
        """
        logger.info(f"Embedding {len(chunks)} chunks")
        
        # Prepare texts for embedding
        texts = []
        chunk_ids = []
        
        for chunk in chunks:
            # Create rich context for embedding
            embedding_text = self._create_embedding_text(chunk)
            texts.append(embedding_text)
            chunk_ids.append(chunk.chunk_id)
        
        # Generate embeddings
        embeddings = self.generate_batch_embeddings(texts, batch_size=batch_size)
        
        # Create mapping
        embedding_dict = {
            chunk_id: embedding
            for chunk_id, embedding in zip(chunk_ids, embeddings)
        }
        
        logger.info(f"Generated {len(embedding_dict)} embeddings")
        return embedding_dict
    
    def _create_embedding_text(self, chunk: ContentChunk) -> str:
        """
        Create optimized text for embedding.
        
        Args:
            chunk: Content chunk
            
        Returns:
            Optimized text for embedding
        """
        parts = []
        
        # Add context
        parts.append(f"Class {chunk.class_level} Mathematics")
        parts.append(f"Chapter {chunk.chapter_number}: {chunk.chapter_name}")
        
        if chunk.section_name:
            parts.append(f"Section: {chunk.section_name}")
        
        # Add content type
        parts.append(f"[{chunk.content_type.value.upper()}]")
        
        # Add main content
        parts.append(chunk.text_content)
        
        # Add equations
        if chunk.latex_equations:
            parts.append("Equations:")
            for eq in chunk.latex_equations[:3]:  # Limit to first 3
                parts.append(eq.latex)
        
        # Add table info
        if chunk.tables:
            for table in chunk.tables:
                parts.append(f"Table: {table.markdown_content[:200]}")  # First 200 chars
        
        # Add image descriptions
        if chunk.images:
            for img in chunk.images:
                if img.description:
                    parts.append(f"Figure: {img.description}")
                if img.ocr_text:
                    parts.append(img.ocr_text[:100])  # First 100 chars
        
        # Combine all parts
        full_text = "\n".join(parts)
        
        # Truncate if too long (keep first and last parts)
        max_length = 500  # Max length for embedding
        if len(full_text) > max_length:
            half = max_length // 2
            full_text = full_text[:half] + "\n...\n" + full_text[-half:]
        
        return full_text
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension
    
    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding
            emb2: Second embedding
            
        Returns:
            Similarity score (0-1)
        """
        # Assuming embeddings are already normalized
        similarity = np.dot(emb1, emb2)
        return float(similarity)
    
    def compute_batch_similarities(
        self,
        query_embedding: np.ndarray,
        embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute similarities between query and multiple embeddings.
        
        Args:
            query_embedding: Query embedding vector
            embeddings: Matrix of embeddings (n_samples, dimension)
            
        Returns:
            Array of similarity scores
        """
        # Cosine similarity via dot product (if normalized)
        similarities = np.dot(embeddings, query_embedding)
        return similarities