import re
import sys

def post_process_answer(text: str) -> str:
    import re
    
    # 0. Placeholder-based protection for LaTeX
    latex_placeholders = {}
    
    def protect_latex(match):
        placeholder = f"__LATEX_PH_{len(latex_placeholders)}__"
        latex_placeholders[placeholder] = match.group(0)
        return placeholder

    text = re.sub(r'\$\$.*?\$\$', protect_latex, text, flags=re.DOTALL)
    text = re.sub(r'\$.*?\$', protect_latex, text)
    
    text = text.replace('— -', '\n\n')
    text = re.sub(r'\s*(#{3,4})\s*', r'\n\n\1 ', text)
    text = re.sub(r'([^>\n])\s*([\*\-])\s+', r'\1\n\2 ', text)
    text = re.sub(r'([^>\n])\s+(\d+\.\s)', r'\1\n\2', text)
    text = re.sub(r'([^>\n])\s*(Step \d+:)', r'\1\n\n**\2**', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    for placeholder, original in latex_placeholders.items():
        if original.startswith('$$'):
            replacement = f"\n\n{original}\n\n"
            text = text.replace(placeholder, replacement)
        else:
            text = text.replace(placeholder, original)
    
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

# Text with blockquote and bullets
bad_text = r"""### Sets Introduction
#### Properties of Sets
- A set is a collection.
- It is unique.
#### 📝 Step-by-Step Solution:
> 1. Identify the universal set $U$.
> 2. Find elements not in $A$.
> 3. List them as $A'$.
#### ✅ Final Answer: $A' = \{2, 4, 6\}$."""

print("--- ORIGINAL ---")
print(bad_text)
print("\n--- PROCESSED ---")
processed = post_process_answer(bad_text)
print(processed)

with open("debug_output.txt", "w", encoding="utf-8") as f:
    f.write(processed)

sys.stdout.flush()
