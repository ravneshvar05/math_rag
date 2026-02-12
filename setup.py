from setuptools import setup, find_packages

setup(
    name="math_rag",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "groq",
        "pymupdf",
        "pdfplumber",
        "pytesseract",
        "sentence-transformers",
        "faiss-cpu",
        "numpy",
        "pandas",
        "pyyaml",
        "python-dotenv",
        "pillow",
    ],
)
