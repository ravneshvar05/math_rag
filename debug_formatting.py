import re
import sys

def post_process_answer(text: str) -> str:
    # 0. Clean up potential weird artifacts like "— -"
    text = text.replace('— -', '\n\n')
    
    # 1. Force newlines before Headers (### or ####)
    text = re.sub(r'\s*(#{3,4})\s*', r'\n\n\1 ', text)
    
    # 2. Force newlines before Bullet Points (* or -)
    text = re.sub(r'([^\n])\s*([\*\-])\s+', r'\1\n\2 ', text)
    
    # 3. Force newlines before Numbered Lists (1., 2., etc.)
    text = re.sub(r'([^\n])\s+(\d+\.\s)', r'\1\n\2', text)
    
    # 4. Fix "Step X:" patterns that might be inline
    text = re.sub(r'([^\n])\s*(Step \d+:)', r'\1\n\n**\2**', text)
    
    # 5. Clean up excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

# Text provided by user that failed to format correctly
bad_text = """Example 2: Finding Complement of a Set #### 🎯 Goal: Find the complement of the set A = {1, 3, 5, 7, 9} in the universal set U = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}. #### 💡 Key Concept: The complement of a set A, denoted by A′, is the set of all elements in the universal set U that do not belong to A. #### 📝 Step-by-Step Solution: 1. Identify the universal set U and the set A. 2. List all elements in U that do not belong to A. 3. The set of elements from step 2 is the complement of A, denoted by A′. #### ✅ Final Answer: A′ = {2, 4, 6, 8, 10}. #### 🚀 Pro Tip: Remember, the complement of a set A is also a subset of the universal set U. ### Example 3: Finding Complement of a Set of Students #### 🎯 Goal: Find the complement of the set A, where A is the set of all girls in Class XI of a coeducational school."""

print("--- ORIGINAL ---")
print(bad_text)
print("\n--- PROCESSED ---")
print(post_process_answer(bad_text))
sys.stdout.flush()
