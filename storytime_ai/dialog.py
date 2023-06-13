"""
Dialog class
============

"""
from .choice import Choice
import re
import os


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

    @classmethod
    def from_markdown(cls, markdown: str):
        """Create a Dialog object from a markdown string.

        Parameters
        ----------
        markdown : str
            The markdown string to parse.
        """
        # Use only the last heading as dialogid
        markdown = markdown.split("\n## ")[-1]
        if not markdown.startswith("## "):
            markdown = "## " + markdown
        lines = markdown.split("\n")
        dialogid = ""
        text = ""
        choices = {}
        choicetext = ""
        nextdialogid = ""
        logic = ""
        for line in lines:
            if line == "":
                pass
            elif line.startswith("# "):
                print("WARNING! Title given in markdown string. This is ignored.")
                pass
            elif line.startswith("## "):
                if dialogid != "":
                    print("WARNING: multiple dialog ids found in markdown string.")
                    break
                dialogid = line[3:].strip()
            elif line.startswith("LOGIC "):
                logic += line[6:] + "\n"
            elif line.startswith("- "):
                if nextdialogid != "":
                    # a new choice is found, so the previous one is added to the dictionary
                    choices[nextdialogid] = Choice(choicetext, nextdialogid)
                x = re.search(r"- (.+): (.+)", line)
                if x is not None:
                    nextdialogid = x.group(1).strip()
                    choicetext = x.group(2).strip()
            elif len(nextdialogid) > 0:
                # the line is in the choices section
                choicetext += "\n" + line
            else:
                # then line is in the dialog section
                text += line + "\n"
        if len(nextdialogid) > 0:
            choices[nextdialogid] = Choice(choicetext, nextdialogid)
        if len(logic) > 0 and logic[-1] == "\n":
            logic = logic[:-1]
        return cls(dialogid, text, choices, logic)

    def __eq__(self, other):
        """Equal operator for the Dialog object.

        Empty lines are ignored and leading and trailing spaces are removed.
        """
        a = self.to_markdown()
        b = other.to_markdown()
        a = os.linesep.join([s.strip() for s in a.splitlines() if s])
        b = os.linesep.join([s.strip() for s in b.splitlines() if s])
        return a == b
