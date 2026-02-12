"""Data schemas for Math RAG system."""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ContentType(Enum):
    """Types of academic content."""
    DEFINITION = "definition"
    THEOREM = "theorem"
    PROOF = "proof"
    DERIVATION = "derivation"
    EXAMPLE = "example"
    EXERCISE = "exercise"
    SOLUTION = "solution"
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    FORMULA = "formula"


class ImageType(Enum):
    """Types of images."""
    DIAGRAM = "diagram"
    GRAPH = "graph"
    CHART = "chart"
    EQUATION = "equation"
    TEXT = "text"
    MIXED = "mixed"


@dataclass
class ImageData:
    """Image metadata and information."""
    image_id: str
    image_path: str
    image_type: ImageType
    description: str = ""
    contains_text: bool = False
    ocr_text: str = ""
    page_number: int = 0
    bbox: Optional[List[float]] = None  # [x0, y0, x1, y1]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['image_type'] = self.image_type.value
        return data


@dataclass
class TableData:
    """Table metadata and content."""
    table_id: str
    table_path: str
    markdown_content: str
    csv_content: Optional[str] = None
    num_rows: int = 0
    num_cols: int = 0
    has_header: bool = False
    contains_math: bool = False
    page_number: int = 0
    bbox: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EquationData:
    """Mathematical equation data."""
    equation_id: str
    latex: str
    original_text: str = ""
    is_inline: bool = False
    is_multiline: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ContentChunk:
    """Main content chunk with comprehensive metadata."""
    
    # Identification
    chunk_id: str
    document_id: str
    
    # Academic Structure
    class_level: str  # "11" or "12"
    chapter_number: int
    chapter_name: str
    section_name: str = ""
    subsection_name: str = ""
    
    # Content Classification
    content_type: ContentType = ContentType.TEXT
    
    # Location
    page_number: int = 0
    page_numbers: List[int] = field(default_factory=list)
    
    # Main Content
    text_content: str = ""
    
    # Mathematical Content
    latex_equations: List[EquationData] = field(default_factory=list)
    has_equation: bool = False
    equation_count: int = 0
    
    # Visual Content
    images: List[ImageData] = field(default_factory=list)
    has_image: bool = False
    image_count: int = 0
    
    # Tabular Content
    tables: List[TableData] = field(default_factory=list)
    has_table: bool = False
    table_count: int = 0
    
    # Exercise Specific
    exercise_number: Optional[int] = None
    question_number: Optional[str] = None
    is_exercise: bool = False
    is_exercise: bool = False
    is_solution: bool = False
    
    # Example Specific
    example_number: Optional[str] = None
    is_example: bool = False
    
    # Content Flags
    contains_proof: bool = False
    contains_derivation: bool = False
    is_definition: bool = False
    is_theorem: bool = False
    
    # Metadata
    token_count: int = 0
    char_count: int = 0
    complexity_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary for storage."""
        data = asdict(self)
        data['content_type'] = self.content_type.value
        data['latex_equations'] = [eq.to_dict() for eq in self.latex_equations]
        data['images'] = [img.to_dict() for img in self.images]
        data['tables'] = [tbl.to_dict() for tbl in self.tables]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentChunk':
        """Create chunk from dictionary."""
        # Convert enums and nested objects
        data['content_type'] = ContentType(data['content_type'])
        
        if 'latex_equations' in data:
            data['latex_equations'] = [
                EquationData(**eq) if isinstance(eq, dict) else eq 
                for eq in data['latex_equations']
            ]
        
        if 'images' in data:
            data['images'] = [
                ImageData(**{**img, 'image_type': ImageType(img['image_type'])}) 
                if isinstance(img, dict) else img
                for img in data['images']
            ]
        
        if 'tables' in data:
            data['tables'] = [
                TableData(**tbl) if isinstance(tbl, dict) else tbl
                for tbl in data['tables']
            ]
        
        return cls(**data)
    
    def get_full_context(self) -> str:
        """Get full text context including all content."""
        context_parts = []
        
        # Add location context
        context_parts.append(f"Class {self.class_level} | Chapter {self.chapter_number}: {self.chapter_name}")
        if self.section_name:
            context_parts.append(f"Section: {self.section_name}")
        
        # Add content type
        context_parts.append(f"Content Type: {self.content_type.value.upper()}")
        
        # Add main text
        context_parts.append(f"\n{self.text_content}")
        
        # Add equations
        if self.latex_equations:
            context_parts.append("\nEquations:")
            for eq in self.latex_equations:
                context_parts.append(f"  {eq.latex}")
        
        # Add table references
        if self.tables:
            context_parts.append(f"\n[Contains {len(self.tables)} table(s)]")
        
        # Add image references
        if self.images:
            context_parts.append(f"\n[Contains {len(self.images)} image(s)]")
            for img in self.images:
                if img.description:
                    context_parts.append(f"  - {img.description}")
        
        return "\n".join(context_parts)


@dataclass
class RetrievalResult:
    """Result from retrieval system."""
    chunk: ContentChunk
    score: float
    rank: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'chunk': self.chunk.to_dict(),
            'score': self.score,
            'rank': self.rank
        }