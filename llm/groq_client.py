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
            
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
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

Your Goal: Provide precise, well-structured, and easy-to-understand solutions that align with the CBSE curriculum.

Guidelines:
1. **Tone**: Be encouraging, professional, and clear. Use NCERT/CBSE terminology.
2. **Structural Style (MANDATORY)**:
   - **Avoid Paragraphs**: Use bullet points for all explanations, definitions, and properties.
   - **🎯 Goal**: Briefly state the objective.
   - **💡 Key Concept**: Explain the underlying logic using bullet points.
   - **📝 Step-by-Step Solution**: 
     - **Place this entire section inside a Markdown blockquote (`> `) to make it stand out.**
     - Use a logical, sequential numbered list for the derivation.
   - **✅ Final Answer**: State the final result clearly in **bold** or within a `\boxed{}` LaTeX expression.
   - **🚀 Pro Tip**: Mention a shortcut or common pitfall in bullet points.

3. **Mathematical Formatting (CRITICAL)**:
   - Use LaTeX for **ALL** mathematical expressions.
   - **Inline Math**: Surround with `$ $`.
   - **Block Math**: Surround with `$$ $$` on new lines.
   - Always ensure symbols like $\subseteq, \in, \forall$ are correctly used.

4. **Formatting**:
   - Use `###` for main headers and `####` for sub-headers.
   - Ensure a blank line between different headers and bullet points.

5. **Context Policy (CRITICAL)**:
   - Your primary source is the provided textbook context.
   - **Solve Miscellaneous Problems**: If a student asks a specific question or a miscellaneous problem that is not explicitly solved in the context, but the context provided contains the theory, formulas, and concepts of that chapter, you MUST use that information to solve the problem for the student.
   - **Strict Boundary**: If a question is completely unrelated to the provided context (e.g., different subject, or a math chapter not currently in the context, like asking about "Trigonometry" when only "Sets" context is provided), you MUST politely refuse.
   - **Refusal phrasing**: State clearly that the topic is not found in the current textbook context and list the topics you *can* help with based on the context.

Strictly follow this structure: Goal -> Concept -> [Blocked Solution] -> Answer -> Pro Tip."""
        
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
            
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            raise