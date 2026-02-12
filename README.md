# Math RAG

A flexible RAG system optimized for mathematical content, supporting PDF extraction, OCR, and structure-aware chunking.

## Features
- **PDF Extraction**: Uses PyMuPDF and pdfplumber.
- **OCR Support**: Tesseract integration for image-based text.
- **Structure-Aware Chunking**: Preserves academic unit boundaries.
- **Hybrid Retrieval**: Combines vector search with metadata filtering.
- **LLM Integration**: Built with Groq API.

## Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables: `cp .env.example .env`

## Usage
See [QUICKSTART.md](QUICKSTART.md) for details.
