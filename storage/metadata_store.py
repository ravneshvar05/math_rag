import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MetadataStore:
    def __init__(self, storage_path: str = "data/metadata.json"):
        self.storage_path = Path(storage_path)
        self.data = self._load()

    def _load(self):
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_chunks(self, chunks: list):
        """Add chunks to metadata store."""
        for chunk in chunks:
            self.data[chunk.chunk_id] = chunk.to_dict()
        logger.info(f"Added {len(chunks)} chunks to metadata store")

    def get_chunk(self, chunk_id: str) -> dict:
        """Get chunk metadata by ID."""
        return self.data.get(chunk_id)

    def get_stats(self) -> dict:
        """Get metadata store statistics."""
        return {
            'total_chunks': len(self.data),
            'storage_path': str(self.storage_path)
        }

    def filter_chunks(self, **kwargs) -> list:
        """
        Filter chunks by metadata fields.
        
        Args:
            **kwargs: Key-value pairs to filter by (e.g., class_level='11')
            
        Returns:
            List of matching chunks (dicts)
        """
        results = []
        for chunk in self.data.values():
            match = True
            for key, value in kwargs.items():
                if chunk.get(key) != value:
                    match = False
                    break
            if match:
                results.append(chunk)
        return results

    def list_documents(self) -> list:
        """
        List all indexed documents with statistics.
        
        Returns:
            List of document summaries
        """
        docs = {}
        for chunk in self.data.values():
            doc_id = chunk.get('document_id', 'unknown')
            if doc_id not in docs:
                docs[doc_id] = {
                    'document_id': doc_id,
                    'class_level': chunk.get('class_level'),
                    'total_chunks': 0,
                    'chapters': set()
                }
            docs[doc_id]['total_chunks'] += 1
            if chunk.get('chapter_name'):
                docs[doc_id]['chapters'].add(
                    f"Chapter {chunk.get('chapter_number')}: {chunk.get('chapter_name')}"
                )
        
        # Convert sets to lists and format output
        result = []
        for doc in docs.values():
            doc['chapters'] = sorted(list(doc['chapters']))
            result.append(doc)
        return result

    def delete_document(self, document_id: str) -> list:
        """
        Delete all chunks associated with a document.
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            List of deleted chunk IDs
        """
        deleted_ids = []
        new_data = {}
        
        for chunk_id, chunk in self.data.items():
            if chunk.get('document_id') == document_id:
                deleted_ids.append(chunk_id)
            else:
                new_data[chunk_id] = chunk
        
        if deleted_ids:
            self.data = new_data
            self.save()
            logger.info(f"Deleted document {document_id} ({len(deleted_ids)} chunks)")
            
        return deleted_ids

