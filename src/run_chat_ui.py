#!/usr/bin/env python
"""
TimenestAI Chat UI Runner

This script launches the Gradio UI for the TimenestAI chat application.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the Gradio UI app
from app.chat_ui import demo

# Run the Gradio app
if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run the TimenestAI Chat UI")
    parser.add_argument("--share", action="store_true", help="Create a shareable link")
    parser.add_argument("--port", type=int, default=7860, help="Port to run the UI on")
    args = parser.parse_args()
    
    # Launch the UI
    print(f"Starting TimenestAI Chat UI on port {args.port}...")
    demo.launch(server_port=args.port, share=args.share) 