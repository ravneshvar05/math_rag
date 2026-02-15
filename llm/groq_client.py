"""Groq LLM client for generation."""

import os
from groq import Groq, RateLimitError, APIConnectionError, InternalServerError
from typing import List, Dict, Any, Optional
from utils.logging import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = get_logger(__name__)


class GroqClient:
    """Client for Groq LLM API with multi-key rotation support."""
    
    def __init__(
        self,
        api_key: str, # Main key passed from config/env typically, but we will look for others too
        model: str = "llama-3.1-70b-versatile",
        temperature: float = 0.1,
        max_tokens: int = 2048
    ):
        """
        Initialize Groq client.
        
        Args:
            api_key: Primary Groq API key
            model: Model name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
        """
        self.output_model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Collect all available API keys from environment
        self.api_keys = []
        
        # Add primary key if provided
        if api_key:
            self.api_keys.append(api_key)
            
        # Check for fallback keys
        # We look for GROQ_API_KEY_2 up to GROQ_API_KEY_5
        for i in range(2, 6):
            key = os.getenv(f"GROQ_API_KEY_{i}")
            if key:
                self.api_keys.append(key)
        
        if not self.api_keys:
            raise ValueError("No Groq API keys found. Please set GROQ_API_KEY in environment.")
            
        logger.info(f"Initialized Groq client with {len(self.api_keys)} API keys available.")
        logger.info(f"Model: {self.output_model}")
        
    def _get_client(self, api_key: str) -> Groq:
        """Helper to create a client instance for a specific key."""
        return Groq(api_key=api_key)

    def _completion_with_fallback(self, create_completion_func, **kwargs) -> Any:
        """
        Execute a completion request with fallback to other API keys on failure.
        
        Args:
            create_completion_func: Lambda or function that takes a client and returns a response
            **kwargs: Arguments to pass to the completion function (like messages, model, etc)
        """
        last_exception = None
        
        for i, api_key in enumerate(self.api_keys):
            try:
                # Create a fresh client for this key to ensure no stale state
                # (Though Groq client is stateless, this is cleaner for rotation)
                client = self._get_client(api_key)
                
                # Execute the specific completion logic
                return create_completion_func(client)
                
            except (RateLimitError, APIConnectionError, InternalServerError) as e:
                logger.warning(f"Groq API error with key {i+1}/{len(self.api_keys)}: {type(e).__name__} - {str(e)}")
                logger.warning("Rotating to next API key...")
                last_exception = e
                continue
            except Exception as e:
                # For input validation errors or other non-transient errors, don't rotate
                logger.error(f"Unrecoverable Groq API error: {e}")
                raise e
                
        # If we get here, all keys failed
        logger.error("All Groq API keys exhausted.")
        if last_exception:
            raise last_exception
        raise RuntimeError("Unknown error: All API keys failed without specific exception.")

    @retry(
        retry=retry_if_exception_type((RateLimitError, APIConnectionError, InternalServerError)),
        stop=stop_after_attempt(2), # Retry the *whole rotation process* twice if needed
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate response from prompt.
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
        
        def _do_generate(client):
            response = client.chat.completions.create(
                model=self.output_model,
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
            
        return self._completion_with_fallback(_do_generate)
    
    @retry(
        retry=retry_if_exception_type((RateLimitError, APIConnectionError, InternalServerError)),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_with_context(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response with retrieved context.
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
            
            if chunk.get('images'):
                context_parts.append(f"\n[Contains {len(chunk['images'])} image(s)]")
                for img in chunk['images']:
                    if img.get('description'):
                        context_parts.append(f"  - {img['description']}")
            
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

5. **Visualizations (PLOTS & GRAPHS)**:
   - **Trigger**: IF and ONLY IF the user explicitly requests a plot/graph OR the question implicitly demands a visual solution.
   - **Constraint**:
     - **Allowed**: You MAY generate plots for any standard mathematical concept.
     - **Context Priority**: Use provided Context data if asked.
     - **Strict Refusal**: Do NOT generate plots for non-academic topics.
   - **Action**: Generate a Python code block to create the plot using `matplotlib` and `seaborn`.
   - **Format**: 
     - Precede the code block with: `### Visualization`
     - Start the code block with: `\`\`\`python # PLOT`
     - The code must be self-contained. Use `plt.title`, `plt.xlabel`, `plt.ylabel`, `plt.grid(True)`.
     - **CRITICAL**: For coordinate geometry, ALWAYS include `plt.axhline(0, color='black', linewidth=1)` and `plt.axvline(0, color='black', linewidth=1)`.
     - Do NOT call `plt.show()`, just create the plot.

6. **Context Policy (CRITICAL)**:
   - Your primary source is the provided textbook context.
   - **Solve Miscellaneous Problems**: If a student asks a specific question or a miscellaneous problem that is not explicitly solved in the context, but the context provided contains the theory, formulas, and concepts of that chapter, you MUST use that information to solve the problem for the student.
   - **Strict Boundary**: If a question is completely unrelated to the provided context, you MUST politely refuse.
   - **Refusal phrasing**: State clearly that the topic is not found in the current textbook context.

Strictly follow this structure: Goal -> Concept -> [Blocked Solution] -> [Visualization if applicable] -> Answer -> Pro Tip."""
        
        full_prompt = f"""Context from textbook:

{context_str}

Student Question: {query}

Please provide a comprehensive answer based on the context above."""
        
        return self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt or default_system
        )
    
    @retry(
        retry=retry_if_exception_type((RateLimitError, APIConnectionError, InternalServerError)),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def create_chat_history(
        self,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Generate response with chat history.
        """
        def _do_chat(client):
            response = client.chat.completions.create(
                model=self.output_model,
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
            
        return self._completion_with_fallback(_do_chat)