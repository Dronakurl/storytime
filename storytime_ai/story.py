"""
Story class
===========

This module contains the classes that represent a story.
A Story is a collection of Dialogs.
A Dialog contains a selection of Choices.
The Story class is responsible for handling the Story with logic

.. code-block:: python

    from storytime_ai import Story
    Story.from_markdown_file("storytime_ai/template/story.md")

"""
import asyncio
from importlib.resources import files
import os
from pathlib import Path
import re
import sys

from .choice import Choice
from .dialog import Dialog
from .require_decorator import Requirement, requires

try:
    import networkx as nx
except ImportError:
    _graph = False
else:
    _graph = True

try:
    import matplotlib.pyplot as plt
except ImportError:
    _plot = False
else:
    _plot = True

try:
    import openai
except ImportError:
    _openai = False
else:
    _openai = True
    from dotenv import load_dotenv

    load_dotenv()
    apikey = os.getenv("OPENAI_API_KEY")
    if apikey is None:
        # read from .env file
        print("OPENAI_API_KEY not set")
        _openai = False
    openai.api_key = apikey


networkx_req = Requirement("networkx", _graph, "Network graph", raise_error=True)
matplotlib_req = Requirement("matplotlib", _plot, "Plotting the graph", raise_error=True)
openai_req = Requirement("openai", _openai, "OpenAI API", raise_error=True)


class Story:
    """
    A class used to represent a Story for navigation, generation and visualization.

    Attributes
    ----------
    title : str
        The title of the story
    dialogs : dict[str, Dialog]
        A dictionary of Dialog objects with the heading of each dialogue as key
    currentdialog : str
        Heading of the current dialog
    prevdialogids : list[str]
        List of headings of previous dialogs, provides a history of the story so far
    markdown_file : str
        Path to the markdown file where the story was loaded or saved
    messages : list[dict[str, str]]
        ChatGPT message history, will be modified by the methods, not only appended
    properties : dict[str, str]
        A dictionary of properties that can be used in the logic of the story
    G: networkx.Graph
        A networkx graph of the story

    """

    storytemplate = files("storytime_ai.templates").joinpath("minimal.md").read_text()

    defaultprompt = "Eine Geschichte über ein Kind, dass im Wald verloren geht"

    def __init__(self, dialogs: dict[str, Dialog], title: str = "Story"):
        """
        Parameters
        ----------
        dialogs : dict[str, Dialog]
            A dictionary of Dialog objects with the heading of each dialogue as key
        title : str, optional
            The title of the story
        """

        self.title = title
        self.dialogs = dialogs
        self.currentdialog = self.dialogs[list(dialogs.keys())[0]]
        self.prevdialogids = [list(dialogs.keys())[0]]
        self.markdown_file = "story.md"
        self.messages = []
        self.properties = {}
        self.exec_logic()
        self.G = None

    def __repr__(self):
        return self.to_markdown()

    def __eq__(self, other):
        return self.to_markdown() == other.to_markdown()

    def next_dialog(self, nextdialogid: str):
        """
        Changes the current dialog to the one with the heading nextdialogid

        Parameters
        ----------
        nextdialogid : str
            The heading of the next dialog
        """
        if nextdialogid not in self.dialogs:
            raise ValueError(f"Dialog {nextdialogid} not found")
        if self.currentdialog.dialogid != self.prevdialogids[-1]:
            self.prevdialogids.append(self.currentdialog.dialogid)
        self.currentdialog = self.dialogs[nextdialogid]
        logmsg = self.currentdialog.logic
        self.exec_logic()
        return logmsg

    def exec_logic(self):
        """
        Executes the logic of the current dialog

        The logic is a string with keywords PROPERTY and NEXTDIALOG.
        They are interpreted such that the properties are set and checked.
        PROPERTY "name" = "value" sets the property "name" to "value".
        NEXTDIALOG "heading" IF "condition" sets the next dialog to "heading" if "condition" is true.
        """
        if len(self.currentdialog.logic) <= 1:
            return
        # loop over lines of logic and interpret the keywords
        for strl in self.currentdialog.logic.split("\n"):
            if strl.startswith("PROPERTY"):
                x = re.search(r"PROPERTY [\"\'](.*)[\"\'] = (.*)", strl)
                try:
                    res = x.group(2)
                    for key in self.properties:
                        res = re.sub(f"[\"']{key}[\"']", f"properties['{key}']", res)
                    self.properties[x.group(1)] = eval(res, {"__builtins__": None}, {"properties": self.properties})
                except Exception as e:
                    print(f"Error {e} in logic {strl}")
            elif strl.startswith("NEXTDIALOG"):
                x = re.search(r"NEXTDIALOG [\"\'](.*)[\"\'] IF (.*)", strl)
                try:
                    cond = x.group(2)
                    for key in self.properties:
                        cond = re.sub(f"[\"']{key}[\"']", f"properties['{key}']", cond)
                    if eval(cond, {"__builtins__": None}, {"properties": self.properties}):
                        # self.currentdialog.choices = {x.group(1): Choice("Continue", x.group(1))}
                        self.next_dialog(x.group(1))
                except Exception as e:
                    print(f"Error {e} in logic {strl}")

    def simpleplay(self):
        """
        Play the story in the command line. No textual, just like Zork.
        """
        while True:
            print("")
            print("*****************************************************")
            print(">>>>" + self.currentdialog.dialogid + "\n")
            print(self.currentdialog.text)
            print("*****************************************************")
            print("")
            if len(self.currentdialog.choices) == 0:
                input("Press enter to end")
                break
            print(f"Choices:")
            choices = dict(enumerate([(k, v) for (k, v) in self.currentdialog.choices.items()]))
            for i, choice in choices.items():
                print(f"[{i}] = {choice[0]}: {choice[1].text}")
            choice = input("Choose: ")
            invalid = False
            if not choice.isdigit():
                invalid = True
            try:
                choice = int(choice)
            except ValueError:
                invalid = True
            if choice not in choices:
                invalid = True
            if invalid:
                print("*****************************************************")
                print(f"Invalid choice! Choose one of {list(choices.keys())}")
                print("*****************************************************")
                continue
            self.continue_story(choices[choice][0], override_existing=False)
            # self.next_dialog(choices[choice][0])

    def addchoice(self, text: str, nextdialogid: str):
        """
        Adds a choice to the current dialog

        Parameters
        ----------
        text : str
            The text of the choice
        nextdialogid : str
            The heading of the next dialog
        """
        self.currentdialog.addchoice(text, nextdialogid)

    def back_dialog(self):
        """
        Changes the current dialog to the previous one, based on the history of visited dialogs
        """
        if len(self.prevdialogids) > 1:
            prvdiag = self.prevdialogids.pop()
        else:
            prvdiag = self.prevdialogids[0]
        self.currentdialog = self.dialogs[prvdiag]

    def markdown_from_history(self, historylen: int = -1, includelogic: bool = False):
        """Returns the markdown of the history of visited dialogs

        Parameters
        ----------
        historylen : int, optional
            The number of dialogs to include in the history. If -1, all dialogs are included.

        Returns
        -------
        str
            The markdown of the history of visited dialogs. The Dialog.to_markdown() method is used to generate the markdown.
        """
        res = f"# {self.title}\n\n"
        history = self.prevdialogids + [self.currentdialog.dialogid]
        if historylen > 0:
            history = history[-historylen:]
        for diagid in history:
            res += self.dialogs[diagid].to_markdown(includelogic=includelogic) + "\n"
        if includelogic:
            for p in self.properties:
                res += f'LOGIC PROPERTY "{p}" = {self.properties[p]}\n'
        return res.strip()

    def save_markdown(self, fname: str = None):
        """
        Saves the story to a markdown file.

        Parameters
        ----------
        fname : str, optional
            The filename to save the story to.
            If None, the filename in the property markdown_file is used.
            If fname is given, the property markdown_file is set to fname.
        """
        if fname is not None:
            self.markdown_file = fname
        with open(Path(self.markdown_file), "w") as f:
            f.write(self.to_markdown())

    def to_markdown(self):
        """
        Returns the story as a markdown string

        Returns
        -------
        str
            The story as a markdown string
        """
        res = f"# {self.title}\n\n"
        res += "\n\n".join([self.dialogs[x].to_markdown() for x in self.dialogs])
        res = res.strip()
        return res

    @classmethod
    def from_markdown(cls, markdown: str):
        """
        Parse a string with markdown and return an Story object.
        No integrity checks are performed with this method.

        Parameters
        ----------
        markdown : str
            The markdown string to parse

        Returns
        -------
        Story
            The story object
        """
        lines = markdown.split("\n")
        dialogs = {}
        dialogid = ""
        text = ""
        choices = {}
        choicetext = ""
        nextdialogid = ""
        title = ""
        logic = ""
        for line in lines:
            if line == "":
                pass
            elif line.startswith("# "):
                title = line[2:].strip()
            elif line.startswith("## "):
                if len(nextdialogid) > 0:
                    # a new choice is found, so the previous one is added to the dictionary
                    choices[nextdialogid] = Choice(choicetext, nextdialogid)
                if dialogid != "":
                    # a new dialog is found, so the previous one is added to the dictionary
                    if len(logic) > 0 and logic[-1] == "\n":
                        logic = logic[:-1]
                    dialogs[dialogid] = Dialog(dialogid, text, choices, logic)
                    text = ""
                    logic = ""
                    choices = {}
                    nextdialogid = ""
                dialogid = line[3:].strip()
            elif line.startswith("LOGIC "):
                logic += line[6:] + "\n"
            elif line.startswith("- "):
                if nextdialogid != "":
                    # a new choice is found, so the previous one is added to the dictionary
                    choices[nextdialogid] = Choice(choicetext, nextdialogid)
                x = re.search(r"- (.+): (.+)", line)
                if x is not None:
                    # regular expression to find the next dialog id
                    nextdialogid = x.group(1).strip()
                    # regular expression to find the choice text
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
        dialogs[dialogid] = Dialog(dialogid, text, choices, logic)
        return cls(dialogs, title=title)

    @classmethod
    def from_markdown_file(cls, fname: Path | str):
        """
        Parse a markdown file and return an Story object.
        No integrity checks are performed with this method.

        Parameters
        ----------
        fname : Path or str
            The filename of the markdown file to parse

        Returns
        -------
        Story
            The story object
        """
        if isinstance(fname, str):
            fname = Path(fname)
        if not fname.is_file():
            print(f"from_markdown_file: ERROR: {fname} is not a file")
            raise FileExistsError
        with open(fname, "r") as f:
            md = f.read()
            res = cls.from_markdown(md)
            res.markdown_file = str(fname)
            return res

    @requires(networkx_req)
    def create_graph(self):
        """
        Create a networkx graph of the story

        Parameters
        ----------
        """
        self.G = nx.DiGraph()
        for dialogid in self.dialogs:
            self.G.add_node(dialogid)
            # include logic choices
            for line in self.dialogs[dialogid].logic.split("\n"):
                if line.startswith("NEXTDIALOG"):
                    x = re.search(r"NEXTDIALOG [\"\'](.*)[\"\'] IF", line)
                    if x is not None:
                        self.G.add_edge(dialogid, x.group(1))
            # include normal choices
            for choiceid in self.dialogs[dialogid].choices:
                self.G.add_edge(dialogid, choiceid)

    @requires(matplotlib_req, networkx_req)
    def plot_graph(self, graphfname: str = None):
        """
        Plot the story as a graph. If a filename in `graphfname` is given, the graph is saved to that file.
        Otherwise, the graph is shown in a window.

        Parameters
        ----------
        graphfname : str, optional
            The filename to save the graph to.
        """
        self.create_graph()
        nx.draw(self.G, with_labels=True)
        if graphfname is not None:
            plt.savefig(graphfname)
        else:
            plt.show()

    @requires(networkx_req)
    def has_subgraphs(self):
        """
        Check if the story has multiple subgraphs, i.e. multiple stories that are not connected to
        each other by a dialog choice.
        """
        self.create_graph()
        # check if there are subgraphs (i.e. multiple stories)
        return nx.number_weakly_connected_components(self.G) > 1

    def check_integrity(self):
        """
        Check the integrity of the story. This method checks if the story has multiple
        subgraphs and if all the choices are valid.
        """
        if _graph and self.has_subgraphs():
            print("Integrity check failed: The story has multiple subgraphs")
            return False
        # check if all the choices are valid
        for dialogid in self.dialogs:
            for choiceid in self.dialogs[dialogid].choices:
                if choiceid not in self.dialogs:
                    print("Integrity check failed: Impossible choice: " + choiceid + " does not exist")
                    return False
        print("Integrity check passed")
        return True

    def prune_dangling_choices(self):
        """
        Remove choices that point to a dialog that does not exist
        """
        choices_to_remove = []
        for dialogid in self.dialogs:
            for choiceid in self.dialogs[dialogid].choices:
                if choiceid not in self.dialogs:
                    choices_to_remove.append((dialogid, choiceid))
        # Remove dangling choices outside the loop
        for dialogid, choiceid in choices_to_remove:
            self.dialogs[dialogid].choices.pop(choiceid)
        return [c[1] for c in choices_to_remove]

    @requires(networkx_req)
    def restrict_to_largest_substory(self):
        """
        Restrict the story to the largest substory. This method removes all the dialogs and choices
        that are not in the largest substory.
        """
        if _graph and not self.has_subgraphs():
            return
        self.create_graph()
        # find the largest subgraph
        largest_subgraph = max(nx.weakly_connected_components(self.G), key=len)
        # remove all the dialogs that are not in the largest subgraph
        dialogs_to_remove = [d for d in self.dialogs if d not in largest_subgraph]
        for d in dialogs_to_remove:
            self.dialogs.pop(d)
        # remove all the choices that are not in the largest subgraph
        choices_to_remove = []
        for dialogid in self.dialogs:
            for choiceid in self.dialogs[dialogid].choices:
                if choiceid not in self.dialogs:
                    choices_to_remove.append((dialogid, choiceid))
        # Remove dangling choices outside the loop
        for dialogid, choiceid in choices_to_remove:
            self.dialogs[dialogid].choices.pop(choiceid)

    @classmethod
    async def generate_story_from_file(cls, fname: str = "./storytime_ai/templates/story.md", sleep_time: float = 0.1):
        """
        Generate a story from a file for testing purposes without using OpenAI.

        Parameters
        ----------
        fname: str
            The name of the file to read from.
        sleep_time: float
            The time to sleep between each line of the file in seconds

        Yields
        ------
        current_result: str
            The current result of the story
        delta: str
            The string that was just added to the story
        """
        current_result = ""
        with open(fname, "r") as f:
            for line in f:
                await asyncio.sleep(sleep_time)
                delta = line
                current_result += delta
                yield current_result, delta

    @classmethod
    @requires(openai_req)
    async def generate_story(cls, prompt: str = "", **kwargs):
        """
        Generate a story from a prompt.

        Parameters
        ----------
        kwargs:
            Keyword arguments to pass to chatgpt

        Yields
        ------
        current_result: str
            The current result of the story
        delta: str
            The string that was just added to the story
        """
        if len(prompt) == 0:
            prompt = cls.defaultprompt
        completion = openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            # model="text-ada-001",
            messages=[
                {
                    "role": "system",
                    "content": "Write the story for a text based role playing game in the markdown structure of the following example. Each dialogue is identified with its heading. Each choice starts with a hyphen and the heading of the dialogue to which the choice leads. After a colon, the description of the choice starts. Write in the language given in the prompt, but keep the keywords LOGIC, PROPERTIES and NEXTDIALOG in English. \n\n ```\n "
                    + cls.storytemplate
                    + "\n ```\n",
                },
                {"role": "user", "content": prompt},
            ],
            stream=True,
            **kwargs,
        )
        current_result = ""
        async for chunk in await completion:
            delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
            if delta is None:
                delta = ""
            current_result += delta
            yield current_result, delta

    @requires(openai_req)
    def continue_story(self, nextdialogid: str, override_existing: bool = True, **kwargs):
        """
        Continue the story with openai starting with the current dialogue and the next choice.

        Parameters
        ----------
        nextdialogid: str
            The heading of the next dialog
        override_exists: bool
            Whether to override the check if the dialog exists
        kwargs:
            Keyword arguments to pass to chatgpt

        Yields
        ------
        current_result: str
            The current result of the next dialogue
        delta: str
            The string that was just added to the story
        """
        print("Continuing story with openai")
        if not override_existing and nextdialogid in self.dialogs:
            self.next_dialog(nextdialogid)

        storytemplate_without_logic = "\n".join([l for l in self.storytemplate.split("\n") if "LOGIC" not in l])
        if len(self.messages) == 0:
            # If there are no messages, we need to start with a system message
            self.messages = [
                {
                    "role": "system",
                    "content": "You are an author of a story for a text based role playing game. You use the structure of the following example to lead through the story. Each dialogue is identified with its heading. Each choice starts with a hyphen and the heading of the dialogue to which the choice leads. After a colon, the description of the choice starts. You write in the language given in the prompt. \n\n ```\n "
                    + storytemplate_without_logic
                    + "\n ```\n",
                }
            ]
        self.messages.append(
            {
                "role": "user",
                "content": f"The story so far is: \n\n ```\n {self.markdown_from_history(historylen=4)}\n ```\n\nThe user chose the option '{nextdialogid}'\n\n Write the next dialogue for this choice.",
            }
        )
        # TODO : Include the next dialogue if it exists
        # TODO : check if the outcome is valid

        # append to the log file
        # TODO : Change prompt log to a logging handler or make it configurable, optional
        # labels: enhancement, good first issue
        logmsg = "==========================================\n\n".join([str(x) for x in self.messages])
        with open("openai.log", "a") as f:
            f.write(f"**********************************************\n {logmsg}\n\n")

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            stream=True,
            **kwargs,
        )
        current_result = ""
        for chunk in completion:
            delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
            if delta is None:
                delta = ""
            current_result += delta
            print(delta, end="")
            # yield current_result, delta

        self.dialogs[nextdialogid] = Dialog(nextdialogid, current_result, {})
        self.next_dialog(nextdialogid)


def get_story():
    """Helper function for the different command line tools."""
    if len(sys.argv) <= 1:
        print("Please provide a filename")
        sys.exit(1)
    fname = Path(sys.argv[1])
    if not fname.is_file():
        print(f"File not found. Exiting. Given filename: {fname}")
        sys.exit(1)
    return Story.from_markdown_file(fname)


def simpleplay():
    """Play a story in the command line."""
    story = get_story()
    story.simpleplay()


def checkintegrity():
    """
    Check the integrity of a story from a file.

    This method checks if the story has multiple subgraphs and if all the choices are valid.
    This method is used to define a command line tool in the python package.
    """
    story = get_story()
    story.check_integrity()
