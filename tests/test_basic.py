"""Example tests for Math RAG System."""

import pytest
from pathlib import Path
from utils.math_utils import MathDetector, EquationCleaner
from utils.schema import ContentChunk, ContentType


class TestMathDetector:
    """Test mathematical content detection."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.detector = MathDetector()
    
    def test_contains_math_with_latex(self):
        """Test detection of LaTeX commands."""
        text = "The integral \\int_0^1 x dx equals 0.5"
        assert self.detector.contains_math(text) is True
    
    def test_contains_math_with_symbols(self):
        """Test detection of math symbols."""
        text = "The sum ∑ of numbers from 1 to n"
        assert self.detector.contains_math(text) is True
    
    def test_contains_math_with_equation(self):
        """Test detection of equations."""
        text = "Given that x = 5 and y = 3"
        assert self.detector.contains_math(text) is True
    
    def test_no_math_content(self):
        """Test text without math."""
        text = "This is a simple sentence without mathematics"
        assert self.detector.contains_math(text) is False
    
    def test_is_proof(self):
        """Test proof detection."""
        text = "Proof: Let x be a real number. Therefore, we can conclude."
        assert self.detector.is_proof(text) is True
    
    def test_is_derivation(self):
        """Test derivation detection."""
        text = "Step 1: Start with x = 5. Step 2: Add 3 to both sides."
        assert self.detector.is_derivation(text) is True
    
    def test_extract_equations(self):
        """Test equation extraction."""
        text = "The formula is $E = mc^2$ and $$F = ma$$"
        equations = self.detector.extract_equations(text)
        assert len(equations) == 2
        assert equations[0].is_inline is True
        assert equations[1].is_inline is False


class TestEquationCleaner:
    """Test equation cleaning utilities."""
    
    def test_clean_latex(self):
        """Test LaTeX cleaning."""
        latex = "  x  +  y  =  z  "
        cleaned = EquationCleaner.clean_latex(latex)
        assert cleaned == "x + y = z"
    
    def test_extract_formula_name(self):
        """Test formula name extraction."""
        text = "Quadratic Formula: $x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$"
        name = EquationCleaner.extract_formula_name(text)
        assert name == "Quadratic Formula"


class TestContentChunk:
    """Test content chunk schema."""
    
    def test_chunk_creation(self):
        """Test creating a content chunk."""
        chunk = ContentChunk(
            chunk_id="test-123",
            document_id="doc-1",
            class_level="11",
            chapter_number=1,
            chapter_name="Sets",
            content_type=ContentType.DEFINITION,
            text_content="A set is a collection of distinct objects."
        )
        
        assert chunk.chunk_id == "test-123"
        assert chunk.content_type == ContentType.DEFINITION
        assert chunk.has_equation is False
    
    def test_chunk_serialization(self):
        """Test chunk to/from dict."""
        chunk = ContentChunk(
            chunk_id="test-456",
            document_id="doc-2",
            class_level="12",
            chapter_number=2,
            chapter_name="Calculus",
            content_type=ContentType.THEOREM,
            text_content="Test content"
        )
        
        # Convert to dict
        chunk_dict = chunk.to_dict()
        assert isinstance(chunk_dict, dict)
        assert chunk_dict['chunk_id'] == "test-456"
        
        # Convert back to chunk
        restored_chunk = ContentChunk.from_dict(chunk_dict)
        assert restored_chunk.chunk_id == chunk.chunk_id
        assert restored_chunk.content_type == chunk.content_type


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.skipif(
        not Path(".env").exists(),
        reason="Requires .env file with API keys"
    )
    def test_pipeline_initialization(self):
        """Test pipeline can be initialized."""
        from app.pipeline import MathRAGPipeline
        
        pipeline = MathRAGPipeline()
        assert pipeline is not None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])