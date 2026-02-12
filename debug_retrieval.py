
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from storage.metadata_store import MetadataStore
from retrieval.hybrid_retriever import HybridRetriever, QueryClassifier, RetrievalPipeline
from storage.vector_store import FAISSVectorStore
from embeddings.embedding_generator import EmbeddingGenerator

# Force UTF-8 output for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def debug_retrieval():
    config = get_config()
    
    print(f"Loading metadata from: {config.metadata_db_path}")
    metadata_store = MetadataStore(config.metadata_db_path)
    
    # 1. Inspect Stats
    stats = metadata_store.get_stats()
    print("\n--- Metadata Stats ---")
    print(stats)
    
    # 2. Check for examples in metadata
    print("\n--- Checking for Example Metadata ---")
    all_chunks = metadata_store.filter_chunks()
    example_chunks = [c for c in all_chunks if c.get('example_number')]
    
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Chunks with 'example_number': {len(example_chunks)}")
    
    if example_chunks:
        print("\nSample Example Chunks:")
        for c in example_chunks[:5]:
            print(f"- ChunkID: {c['chunk_id']}")
            print(f"  Example Num: {c['example_number']}")
            print(f"  Content Preview: {c['text_content'][:50]}...")
            print("-" * 20)
    else:
        print("WARNING: No chunks have 'example_number' popluated!")
        
    # 3. Simulate Query: 'Example 1' (Testing Hybrid Retrieval)
    print("\n--- Simulating Query: 'Example 1' ---")
    try:
        # Load necessary components for full simulation
        from retrieval.hybrid_retriever import HybridRetriever
        from embeddings.embedding_generator import EmbeddingGenerator
        from storage.vector_store import FAISSVectorStore
        
        # We need a proper config
        config.vector_db_path = Path('data/vector_store')
        config.embedding_model = 'sentence-transformers/all-MiniLM-L6-v2'
        
        # Init components (mocking pipeline init)
        emb_gen = EmbeddingGenerator(config.embedding_model)
        vec_store = FAISSVectorStore.load(config.vector_db_path)
        
        # Init Hybrid Retriever
        retriever_config = {
            'top_k': 5,
            'similarity_threshold': 0.0, # Low threshold to see everything
            'alpha': 0.7,
            'bm25_index_path': 'data/vector_store/bm25.pkl'
        }
        
        hybrid_retriever = HybridRetriever(
            vector_store=vec_store,
            metadata_store=metadata_store,
            embedding_generator=emb_gen,
            config=retriever_config
        )
        
        # Build index for debug
        all_chunks = metadata_store.filter_chunks()
        hybrid_retriever.keyword_retriever.index_chunks(all_chunks)
        
        # Execute Retrieve
        print(f"Query: 'give me example 1'")
        if hybrid_retriever._is_entity_query("give me example 1"):
             print("DEBUG: Entity Query Detected! Alpha should be 0.3")
        else:
             print("DEBUG: Concept Query Detected. Alpha should be 0.7")
             
        results = hybrid_retriever.retrieve("give me example 1")
        
        if results:
            print(f"\nFound {len(results)} results:")
            for r in results:
                print(f"Rank {r.rank}: Score {r.score:.4f} | Chunk {r.chunk.chunk_id}")
                print(f"Content Preview: {r.chunk.text_content[:100]}...")
                print("-" * 20)
        else:
            print("No results found.")

    except Exception as e:
        print(f"Error during simulation: {e}")

    except Exception as e:
        print(f"Error during simulation: {e}")

if __name__ == "__main__":
    debug_retrieval()
