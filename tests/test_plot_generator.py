
import sys
import os
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.plot_generator import PlotGenerator

def test_plot_generator():
    """Test the plot generator utility."""
    print("Testing PlotGenerator...")
    
    # Setup
    output_dir = Path("tests/output")
    generator = PlotGenerator(output_dir)
    
    # Test case 1: Simple Line Plot
    code1 = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 4))
plt.plot(x, y, label='sin(x)')
plt.title('Sine Wave')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
"""
    print("\nExecuting Test Case 1 (Sine Wave)...")
    path1 = generator.execute_plot_code(code1)
    
    if path1 and os.path.exists(path1):
        print(f"✅ Success! Plot saved to: {path1}")
    else:
        print("❌ Failed to generate plot 1")

    # Test case 2: Seaborn Plot
    code2 = """
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

data = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D'],
    'Values': [10, 25, 15, 30]
})

plt.figure(figsize=(6, 4))
sns.barplot(data=data, x='Category', y='Values')
plt.title('Sample Bar Plot')
"""
    print("\nExecuting Test Case 2 (Seaborn Bar Plot)...")
    path2 = generator.execute_plot_code(code2)
    
    if path2 and os.path.exists(path2):
        print(f"✅ Success! Plot saved to: {path2}")
    else:
        print("❌ Failed to generate plot 2")

    # Test case 3: Invalid Code (Should be handled gracefully)
    code3 = """
print("Hello World")
# No plotting here
"""
    print("\nExecuting Test Case 3 (No Plot)...")
    path3 = generator.execute_plot_code(code3)
    
    if path3 is None:
        print("✅ Correctly returned None for no plot.")
    else:
        print(f"❌ Unexpectedly returned path: {path3}")

    # Test case 4: Syntax Error
    code4 = """
plt.plot(x, y  # Missing closing parenthesis
"""
    print("\nExecuting Test Case 4 (Syntax Error)...")
    path4 = generator.execute_plot_code(code4)
    
    if path4 is None:
        print("✅ Correctly handled syntax error.")
    else:
        print(f"❌ Unexpectedly returned path: {path4}")

if __name__ == "__main__":
    test_plot_generator()
