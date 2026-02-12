"""Command-line interface for querying the RAG system."""

import argparse
import sys
from app.pipeline import MathRAGPipeline
from utils.logging import get_logger

logger = get_logger(__name__)


def print_response(response: dict):
    """Print query response in formatted way."""
    print("\n" + "="*80)
    print("ANSWER")
    print("="*80)
    print(response['answer'])
    print("\n" + "="*80)
    print("SOURCES")
    print("="*80)
    
    for i, source in enumerate(response['sources'], 1):
        print(f"\n[{i}] {source['chapter']}")
        if source['section']:
            print(f"    Section: {source['section']}")
        print(f"    Type: {source['content_type']}")
        print(f"    Page: {source['page']}")
        print(f"    Relevance Score: {source['score']:.3f}")
        print(f"    Preview: {source['text_preview']}")
        
        if source['images']:
            print(f"    Images: {len(source['images'])} image(s)")
            for img_path in source['images']:
                print(f"      - {img_path}")
        
        if source['tables']:
            print(f"    Tables: {len(source['tables'])} table(s)")
            for tbl_path in source['tables']:
                print(f"      - {tbl_path}")
    
    print("\n" + "="*80)
    print(f"Confidence: {response['confidence']:.3f}")
    print("="*80 + "\n")


def interactive_mode(pipeline: MathRAGPipeline, args):
    """Run in interactive query mode."""
    print("\n" + "="*80)
    print("MATH RAG SYSTEM - INTERACTIVE MODE")
    print("="*80)
    print("Type your questions. Type 'exit' or 'quit' to stop.")
    print("="*80 + "\n")
    
    while True:
        try:
            # Get query
            query = input("\nYour Question: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\nExiting...")
                break
            
            # Process query
            response = pipeline.query(
                query=query,
                class_level=args.class_level,
                chapter_number=args.chapter,
                top_k=args.top_k
            )
            
            # Print response
            print_response(response)
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            logger.error(f"Query failed: {e}", exc_info=True)
            print(f"\nError: {e}\n")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Math RAG System - Query Mathematics Textbooks"
    )
    
    parser.add_argument(
        '--query',
        '-q',
        type=str,
        help='Query to ask (if not provided, enters interactive mode)'
    )
    
    parser.add_argument(
        '--class',
        dest='class_level',
        type=str,
        choices=['11', '12'],
        help='Filter by class level'
    )
    
    parser.add_argument(
        '--chapter',
        type=int,
        help='Filter by chapter number'
    )
    
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of results to retrieve (default: 5)'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show system statistics'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize pipeline
        logger.info("Initializing Math RAG Pipeline...")
        pipeline = MathRAGPipeline()
        
        # Show stats if requested
        if args.stats:
            stats = pipeline.get_stats()
            print("\n" + "="*80)
            print("SYSTEM STATISTICS")
            print("="*80)
            print("\nMetadata Store:")
            for key, value in stats['metadata'].items():
                print(f"  {key}: {value}")
            print("\nVector Store:")
            for key, value in stats['vector_store'].items():
                print(f"  {key}: {value}")
            print("="*80 + "\n")
            return
        
        # Single query mode
        if args.query:
            logger.info(f"Processing query: {args.query}")
            response = pipeline.query(
                query=args.query,
                class_level=args.class_level,
                chapter_number=args.chapter,
                top_k=args.top_k
            )
            print_response(response)
        else:
            # Interactive mode
            interactive_mode(pipeline, args)
        
    except Exception as e:
        logger.error(f"Application failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()