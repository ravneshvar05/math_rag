
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import io
import uuid
from pathlib import Path
from utils.logging import get_logger
from config import get_config

logger = get_logger(__name__)

class PlotGenerator:
    """Securely executes plotting code and returns the image path."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Verify seaborn style
        sns.set_theme(style="whitegrid")

    def execute_plot_code(self, code: str) -> str:
        """
        Executes the provided Python code to generate a plot.
        
        Args:
            code: Python code string (should use plt or sns)
            
        Returns:
            Absolute path to the generated image file.
            
        Raises:
            ValueError: If code execution fails or no plot is generated.
        """
        # Create a unique filename
        filename = f"plot_{uuid.uuid4().hex}.png"
        filepath = self.output_dir / filename
        
        # Prepare execution environment
        # We strictly limit globals to safe plotting libraries
        local_scope = {}
        global_scope = {
            'plt': plt,
            'sns': sns,
            'pd': pd,
            'np': np,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'range': range,
            'len': len
            # Add other safe builtins as needed
        }
        
        try:
            # Clear any existing plots
            plt.clf()
            
            # Execute the code
            exec(code, global_scope, local_scope)
            
            # Save the figure
            if plt.get_fignums():
                plt.savefig(str(filepath), bbox_inches='tight', dpi=150)
                plt.close('all')
                logger.info(f"Plot generated successfully: {filepath}")
                return str(filepath)
            else:
                logger.warning("Code executed but no figure was created.")
                return None
                
        except Exception as e:
            logger.error(f"Error executing plot code: {e}")
            plt.close('all') # Cleanup
            return None
