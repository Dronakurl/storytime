"""
Stories are a set of Dialogs that are linked together by Choices.

The Story class is the main class for creating stories. It is a container for
Dialogs and Choices. It also contains the main logic for running the story. 

The _openai, _plot, and _graph variables are booleans that indicate whether
the functionality for those features is available. 
"""
import os
from pathlib import Path

from .choice import Choice
from .dialog import Dialog
from .story import Story, _graph, _openai, _plot


def streamlit_app():
    os.system("streamlit run " + str(Path(__file__).parent / "app.py") + " --server.port 8501")
