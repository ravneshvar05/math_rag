import sys
import os
from config import get_config, get_yaml_config
from retrieval.hybrid_retriever import HybridRetriever, RetrievalPipeline

# Add src to path
sys.path.append(os.path.join(os.getcwd(), '.'))

def analyze_retrieval(query):
    print(f"Analyzing retrieval for query: '{query}'")
    
    # Load components
    config = get_config()
    retrieval_config = get_yaml_config('retrieval')
    
    try:
        from storage.vector_store import FAISSVectorStore
        from storage.metadata_store import MetadataStore
        from embeddings.embedding_generator import EmbeddingGenerator
        
        vector_store = FAISSVectorStore.load(config.vector_db_path)
        metadata_store = MetadataStore(config.metadata_db_path)
        embedding_generator = EmbeddingGenerator(
            model_name=config.embedding_model,
            device='cpu' # Force CPU for test
        )
        
        retriever = HybridRetriever(
            vector_store=vector_store,
            metadata_store=metadata_store,
            embedding_generator=embedding_generator,
            config=retrieval_config
        )
        
        pipeline = RetrievalPipeline(retriever=retriever)
        
        # Run search
        results = pipeline.search(query, top_k=5)
        
        print(f"\nFound {len(results)} chunks.")
        
        total_chars = 0
        print("\n--- Chunk Analysis ---")
        for i, res in enumerate(results):
            chunk = res.chunk
            char_len = len(chunk.text_content)
            total_chars += char_len
            print(f"[{i+1}] Score: {res.score:.4f} | ID: {chunk.chunk_id}")
            print(f"    Type: {chunk.content_type}")
            print(f"    Chapter: {chunk.chapter_number} - {chunk.chapter_name}")
            print(f"    Length: {char_len} chars")
            print(f"    Preview: {chunk.text_content[:100]}...")
            if chunk.text_content.lower().count("exercise 3.2"):
                print("    -> Contains 'Exercise 3.2'")
            print("-" * 40)
            
        print(f"\nTotal Context Characters: {total_chars}")
        print(f"Est. Tokens (chars / 4): {total_chars / 4}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_retrieval("Exercise 3.2 questions only")
