"""
Smart Delivery Simulator - Hugging Face Spaces Entry Point
This file serves as the entry point for Hugging Face Spaces deployment.
Hugging Face looks for streamlit_app.py in the root directory.
"""

import sys
import os

# Ensure the root directory is in Python path for proper imports
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import and run the main app directly
# This executes the Streamlit app from ui/app.py
from ui.app import main

# Run the main app function
main()
