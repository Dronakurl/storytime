"""
Stories are a set of Dialogs that are linked together by Choices.

The Story class is the main class for creating stories. It is a container for
Dialogs and Choices. It also contains the main logic for running the story. 

The _openai, _plot, and _graph variables are booleans that indicate whether
the functionality for those features is available. 
"""
from .story import Story, _openai, _plot, _graph
from .dialog import Dialog
from .choice import Choice
from .app import startapp
import os
from pathlib import Path


def streamlit_app():
    os.system("streamlit run " + str(Path(__file__).parent / "webapp.py") + " --server.port 8501")
