"""
Choice class
============
"""
import logging

log = logging.getLogger("st." + __name__)


class Choice:
    """
    Choice class, that represents a choice in a dialog

    Attributes
    ----------
    text : str
        The text of the choice
    nextdialogid : str
        The id of the next dialog, which is the heading of the next dialogue
    """

    def __init__(self, text: str, nextdialogid: str):
        self.nextdialogid = nextdialogid
        self.text = text

    def __repr__(self):
        return f"Choice({self.text}, {self.nextdialogid})"

    def to_markdown(self):
        """Returns the choice in markdown format

        Returns
        -------
        str
        """
        return f"- {self.nextdialogid}: {self.text}"

    def __eq__(self, other):
        return self.to_markdown() == other.to_markdown()
