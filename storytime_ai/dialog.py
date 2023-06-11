"""
Dialog class
============

"""
from .choice import Choice


class Dialog:
    """
    Dialog class, that represents a single dialogue in the story.

    A dialog provides markdown output and can contain logic in a basic syntax.
    This logic is parsed and used by the Story.exec_logic() method.

    Attributes
    ----------
    dialogid : str
        The unique identifier of the dialog. It is a heading in the markdown output.
    text : str
        Dialog text. It is a paragraph in the markdown output. Markdown is supported,
        if the heading level is not higher than three ('###')
    choices : dict[str, Choice]
        A dictionary of Choice objects. The key is the next dialog id (heading),
        the value is the Choice object.
    logic : str
        A string containing the logic. It is parsed by the Story.exec_logic() method.

    """

    def __init__(self, dialogid: str, text: str, choices: dict[str, Choice], logic: str = ""):
        """
        Parameters
        ----------
        dialogid : str
        text : str
        choices : dict[str, Choice]
        logic : str, optional
        """
        self.dialogid = dialogid
        self.text = text
        self.choices = choices
        self.logic = logic

    def addchoice(self, text: str, nextdialogid: str):
        choice = Choice(text, nextdialogid)
        self.choices[choice.nextdialogid] = choice

    def __repr__(self):
        return f"Dialog({self.dialogid}, {self.text}, {self.choices})"

    def choices_to_markdown(self):
        return "\n\n".join([self.choices[x].to_markdown() for x in self.choices])

    def write_logic(self):
        """Write the logic to markdown string.

        Returns
        -------
        str
            The logic as markdown string. each line is prefixed with `LOGIC`
        """
        if self.logic.strip() == "":
            return ""
        return "\n".join([f"LOGIC {x}" for x in self.logic.split("\n")]) + "\n\n"

    def to_markdown(self, includelogic: bool = True):
        """Write the dialog to markdown string.

        Parameters
        ----------
        includelogic : bool, optional
            If True, the logic is included in the markdown output, by default True

        Returns
        -------
        str
            The dialog as markdown string.
        """
        if includelogic:
            return f"## {self.dialogid}\n{self.write_logic()}{self.text}\n{self.choices_to_markdown()}"
        else:
            return f"## {self.dialogid}\n{self.text}\n{self.choices_to_markdown()}"

    def __eq__(self, other):
        return self.to_markdown() == other.to_markdown()
