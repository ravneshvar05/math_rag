# Quick Start Guide

## 1. Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

## 2. Index a Document
```bash
python -m app.index_document --file data/raw/sample.pdf
```

## 3. Query the System
```bash
python -m app.query --question "What is the Pythagorean theorem?"
```
