"""Mathematical content detection and processing utilities."""

import re
from typing import List, Tuple, Dict, Optional
from utils.schema import EquationData


class MathDetector:
    """Detect and extract mathematical content."""
    
    # LaTeX commands and patterns
    LATEX_COMMANDS = [
        r'\\int', r'\\sum', r'\\prod', r'\\lim', r'\\frac',
        r'\\sqrt', r'\\partial', r'\\nabla', r'\\infty',
        r'\\alpha', r'\\beta', r'\\gamma', r'\\delta', r'\\theta',
        r'\\lambda', r'\\mu', r'\\sigma', r'\\pi', r'\\omega',
        r'\\sin', r'\\cos', r'\\tan', r'\\log', r'\\ln', r'\\exp',
        r'\\det', r'\\dim', r'\\ker', r'\\max', r'\\min'
    ]
    
    # Math symbols
    MATH_SYMBOLS = [
        '∫', '∑', '∏', '√', '∞', '∂', '∇',
        'α', 'β', 'γ', 'δ', 'θ', 'λ', 'μ', 'σ', 'π', 'ω',
        '≤', '≥', '≠', '≈', '∈', '∉', '⊂', '⊃', '∪', '∩',
        '×', '÷', '±', '∓', '→', '←', '↔', '⇒', '⇐', '⇔'
    ]
    
    # Equation delimiters
    INLINE_DELIMITERS = [('$', '$'), (r'\(', r'\)')]
    DISPLAY_DELIMITERS = [('$$', '$$'), (r'\[', r'\]')]
    
    def __init__(self):
        """Initialize math detector."""
        self.latex_pattern = '|'.join(self.LATEX_COMMANDS)
        self.symbol_pattern = '[' + ''.join(re.escape(s) for s in self.MATH_SYMBOLS) + ']'
    
    def contains_math(self, text: str) -> bool:
        """Check if text contains mathematical content."""
        if not text:
            return False
        
        # Check for LaTeX commands
        if re.search(self.latex_pattern, text):
            return True
        
        # Check for math symbols
        if re.search(self.symbol_pattern, text):
            return True
        
        # Check for equation patterns
        if re.search(r'[a-zA-Z]\s*[=<>≤≥]\s*', text):
            return True
        
        # Check for fraction patterns
        if re.search(r'\d+/\d+', text):
            return True
        
        return False
    
    def extract_equations(self, text: str) -> List[EquationData]:
        """Extract equations from text."""
        equations = []
        equation_id = 0
        
        # Extract display equations
        for start_delim, end_delim in self.DISPLAY_DELIMITERS:
            pattern = re.escape(start_delim) + r'(.*?)' + re.escape(end_delim)
            for match in re.finditer(pattern, text, re.DOTALL):
                equation_id += 1
                equations.append(EquationData(
                    equation_id=f"eq_{equation_id}",
                    latex=match.group(1).strip(),
                    original_text=match.group(0),
                    is_inline=False,
                    is_multiline='\n' in match.group(1) or '\\\\' in match.group(1)
                ))
        
        # Extract inline equations
        for start_delim, end_delim in self.INLINE_DELIMITERS:
            pattern = re.escape(start_delim) + r'(.*?)' + re.escape(end_delim)
            for match in re.finditer(pattern, text):
                equation_id += 1
                equations.append(EquationData(
                    equation_id=f"eq_{equation_id}",
                    latex=match.group(1).strip(),
                    original_text=match.group(0),
                    is_inline=True,
                    is_multiline=False
                ))
        
        return equations
    
    def calculate_math_density(self, text: str) -> float:
        """Calculate mathematical content density (0-1)."""
        if not text:
            return 0.0
        
        math_chars = 0
        total_chars = len(text)
        
        # Count LaTeX commands
        math_chars += len(re.findall(self.latex_pattern, text)) * 5
        
        # Count math symbols
        math_chars += len(re.findall(self.symbol_pattern, text)) * 2
        
        # Count equations
        for start_delim, end_delim in self.DISPLAY_DELIMITERS + self.INLINE_DELIMITERS:
            pattern = re.escape(start_delim) + r'(.*?)' + re.escape(end_delim)
            for match in re.finditer(pattern, text, re.DOTALL):
                math_chars += len(match.group(1))
        
        return min(math_chars / total_chars, 1.0) if total_chars > 0 else 0.0
    
    def is_proof(self, text: str) -> bool:
        """Check if text is a proof."""
        proof_indicators = [
            r'\bproof\b', r'\bprove\b', r'\bQ\.E\.D\b', r'\b∎\b',
            r'\btherefore\b', r'\bhence\b', r'\bthus\b',
            r'\blet us prove\b', r'\bwe shall prove\b',
            r'\bsolution\b', r'\bproof:\b'
        ]
        
        text_lower = text.lower()
        for indicator in proof_indicators:
            if re.search(indicator, text_lower, re.IGNORECASE):
                return True
        return False
    
    def is_derivation(self, text: str) -> bool:
        """Check if text is a derivation."""
        derivation_indicators = [
            r'\bderive\b', r'\bderivation\b', r'\bderivative\b',
            r'\bstep \d+\b', r'\bfrom.*we get\b', r'\bsubstituting\b',
            r'\bsolving\b', r'\bsimplifying\b', r'\bon solving\b'
        ]
        
        text_lower = text.lower()
        for indicator in derivation_indicators:
            if re.search(indicator, text_lower, re.IGNORECASE):
                return True
        
        # Check for multi-step equations
        if text.count('=') >= 3:
            return True
        
        return False
    
    def detect_content_type(self, text: str) -> str:
        """Detect the type of mathematical content."""
        text_lower = text.lower()
        
        if re.search(r'\bdefinition\b|\bdefine\b|\bdef\.\b', text_lower):
            return 'definition'
        elif re.search(r'\btheorem\b|\bthm\.\b|\blemma\b|\bcorollary\b', text_lower):
            return 'theorem'
        elif self.is_proof(text):
            return 'proof'
        elif self.is_derivation(text):
            return 'derivation'
        elif re.search(r'\bexample\b|\bex\.\b', text_lower):
            return 'example'
        elif re.search(r'\bexercise\b|\bquestion\b|\bq\.\b|\bproblem\b', text_lower):
            return 'exercise'
        elif re.search(r'\bsolution\b|\bsol\.\b|\banswer\b', text_lower):
            return 'solution'
        else:
            return 'text'


class EquationCleaner:
    """Clean and normalize mathematical equations."""
    
    @staticmethod
    def clean_latex(latex: str) -> str:
        """Clean LaTeX equation string."""
        # Remove extra whitespace
        latex = re.sub(r'\s+', ' ', latex).strip()
        
        # Fix common OCR errors
        replacements = {
            'x': '×',  # multiplication
            'α': r'\alpha',
            'β': r'\beta',
            'γ': r'\gamma',
            'θ': r'\theta',
            '∫': r'\int',
            '∑': r'\sum',
            '√': r'\sqrt',
            '∞': r'\infty',
            '≤': r'\leq',
            '≥': r'\geq',
            '≠': r'\neq',
            '≈': r'\approx',
        }
        
        for symbol, latex_cmd in replacements.items():
            latex = latex.replace(symbol, latex_cmd)
        
        return latex
    
    @staticmethod
    def extract_formula_name(text: str) -> Optional[str]:
        """Extract formula name if present."""
        # Pattern: "Formula Name:" or "(Formula Name)"
        patterns = [
            r'^([A-Z][A-Za-z\s]+):\s*',
            r'\(([A-Z][A-Za-z\s]+)\)\s*$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.strip())
            if match:
                return match.group(1).strip()
        
        return None