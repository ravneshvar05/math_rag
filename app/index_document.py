"""Command-line interface for indexing documents."""

import argparse
from pathlib import Path
import sys
from app.pipeline import MathRAGPipeline
from utils.logging import get_logger

logger = get_logger(__name__)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Math RAG System - Index CBSE Mathematics Textbooks"
    )
    
    parser.add_argument(
        'pdf_path',
        type=str,
        help='Path to PDF textbook file'
    )
    
    parser.add_argument(
        '--class',
        dest='class_level',
        type=str,
        required=True,
        choices=['11', '12'],
        help='Class level (11 or 12)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reindexing even if document exists'
    )
    
    args = parser.parse_args()
    
    # Validate PDF path
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        sys.exit(1)
    
    if not pdf_path.suffix.lower() == '.pdf':
        logger.error(f"File is not a PDF: {pdf_path}")
        sys.exit(1)
    
    try:
        # Initialize pipeline
        logger.info("Initializing Math RAG Pipeline...")
        pipeline = MathRAGPipeline()
        
        # Index document
        logger.info(f"Indexing {pdf_path.name} for Class {args.class_level}...")
        stats = pipeline.index_document(
            pdf_path=str(pdf_path),
            class_level=args.class_level,
            force_reindex=args.force
        )
        
        # Print statistics
        print("\n" + "="*80)
        print("INDEXING COMPLETE")
        print("="*80)
        print(f"Document ID: {stats['document_id']}")
        print(f"Class Level: {stats['class_level']}")
        print(f"Total Pages: {stats['total_pages']}")
        print(f"Total Chunks: {stats['total_chunks']}")
        print(f"Total Images: {stats['total_images']}")
        print(f"Total Tables: {stats['total_tables']}")
        print(f"Total Embeddings: {stats['total_embeddings']}")
        print("="*80)
        
        logger.info("Indexing completed successfully")
        
    except Exception as e:
        logger.error(f"Indexing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()