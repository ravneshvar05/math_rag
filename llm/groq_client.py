"""Groq LLM client for generation."""

from groq import Groq
from typing import List, Dict, Any, Optional
from utils.logging import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential

logger = get_logger(__name__)


class GroqClient:
    """Client for Groq LLM API."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-70b-versatile",
        temperature: float = 0.1,
        max_tokens: int = 2048
    ):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key
            model: Model name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.client = Groq(api_key=api_key)
        
        logger.info(f"Initialized Groq client with model: {model}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response from prompt.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_with_context(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response with retrieved context.
        
        Args:
            query: User query
            context_chunks: Retrieved context chunks
            system_prompt: Optional system prompt
            
        Returns:
            Generated response
        """
        # Build context string
        context_parts = []
        
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(f"[Context {i}]")
            context_parts.append(f"Source: Class {chunk['class_level']}, Chapter {chunk['chapter_number']}: {chunk['chapter_name']}")
            
            if chunk.get('section_name'):
                context_parts.append(f"Section: {chunk['section_name']}")
            
            context_parts.append(f"Type: {chunk['content_type']}")
            context_parts.append(f"\nContent:\n{chunk['text_content']}")
            
            # Add equations
            if chunk.get('equations'):
                context_parts.append("\nEquations:")
                for eq in chunk['equations']:
                    context_parts.append(f"  {eq}")
            
            # Add images
            if chunk.get('images'):
                context_parts.append(f"\n[Contains {len(chunk['images'])} image(s)]")
                for img in chunk['images']:
                    if img.get('description'):
                        context_parts.append(f"  - {img['description']}")
                    if img.get('path'):
                        context_parts.append(f"    Image: {img['path']}")
            
            # Add tables
            if chunk.get('tables'):
                context_parts.append(f"\n[Contains {len(chunk['tables'])} table(s)]")
            
            context_parts.append("\n" + "="*80 + "\n")
        
        context_str = "\n".join(context_parts)
        
        # Create prompt
        default_system = """You are a friendly and expert mathematics tutor for CBSE Class 11 and 12 students.

Your Goal: Make the student UNDERSTAND the concept, not just get the answer.

Guidelines:
1. **Tone**: Be encouraging, clear, and patient. Avoid overly academic jargon unless defined.
2. **Structure**:
   - **🎯 Goal**: Briefly state what we need to find.
   - **💡 Key Concept**: Mention the formula or theorem used (if applicable).
   - **📝 Step-by-Step Solution**: Solve the problem logically.
   - **✅ Final Answer**: Clearly state the result.
   - **🚀 Pro Tip**: Add a small tip, common mistake to avoid, or sanity check.

3. **Formatting**:
   - Use `###` for headers.
   - Use **bold** for key terms and numbers.
   - Use LaTeX for ALL math (e.g., $x^2$.
   - Use numbered lists or bullet points for steps.

4. **Context**: Use the provided textbook context as your primary source.

Strictly follow this structure: Goal -> Concept -> Steps -> Answer -> Pro Tip."""
        
        full_prompt = f"""Context from textbook:

{context_str}

Student Question: {query}

Please provide a comprehensive answer based on the context above."""
        
        return self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt or default_system
        )
    
    def create_chat_history(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """
        Generate response with chat history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            raise