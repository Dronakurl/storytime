"""
This module contains the classes that represent a story.
A Story is a collection of Dialogs.
A Dialog contains a selection of Choices.
The Story class is responsible for handling the Story with logic
"""
import os
from pathlib import Path
import re

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
    apikey = os.getenv("OPENAI_API_KEY")
    if apikey is None:
        print("OPENAI_API_KEY not set")
        _openai = False
    openai.api_key = apikey


networkx_req = Requirement("networkx", _graph, "Network graph", raise_error=True)
matplotlib_req = Requirement("matplotlib", _plot, "Plotting the graph", raise_error=True)
openai_req = Requirement("openai", _openai, "OpenAI API", raise_error=True)


class Story:
    with open("data/minimal.md", "r") as f:
        storytemplate = f.read()

    def __init__(self, dialogs: dict[str, Dialog], title: str = "Story"):
        self.dialogs = dialogs
        self.currentdialog = self.dialogs[list(dialogs.keys())[0]]
        self.prevdialogids = [list(dialogs.keys())[0]]
        self.title = title
        self.markdown_file = "story.md"
        self.properties = {}
        self.exec_logic()
        self.G = nx.DiGraph()

    def __repr__(self):
        return self.to_markdown()

    def __eq__(self, other):
        return self.to_markdown() == other.to_markdown()

    def next_dialog(self, nextdialogid: str):
        self.prevdialogids.append(self.currentdialog.dialogid)
        self.currentdialog = self.dialogs[nextdialogid]
        logmsg = self.currentdialog.logic
        self.exec_logic()
        return logmsg

    def exec_logic(self):
        if len(self.currentdialog.logic) <= 1:
            return
        # loop over lines of logic
        for strl in self.currentdialog.logic.split("\n"):
            # # string code that sets the properties
            # strl = "PROPERTY 'Property Key' = 'Property Value'"
            # # string code that changes the current dialog based on the properties
            # strl = "NEXTDIALOG 'Dialog ID' IF 'Property Key' == 'Property Value'"
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
                        print(cond)
                    if eval(cond, {"__builtins__": None}, {"properties": self.properties}):
                        # self.currentdialog.choices = {x.group(1): Choice("Continue", x.group(1))}
                        self.next_dialog(x.group(1))
                except Exception as e:
                    print(f"Error {e} in logic {strl}")

    def addchoice(self, text: str, nextdialogid: str):
        self.currentdialog.addchoice(text, nextdialogid)

    def back_dialog(self):
        print(self.prevdialogids)
        if len(self.prevdialogids) > 1:
            prvdiag = self.prevdialogids.pop()
        else:
            prvdiag = self.prevdialogids[0]
        self.currentdialog = self.dialogs[prvdiag]

    def save_markdown(self, fname: str = None):
        if fname is not None:
            self.markdown_file = fname
        with open(Path(self.markdown_file), "w") as f:
            f.write(self.to_markdown())

    def to_markdown(self):
        res = f"# {self.title}\n\n"
        res += "\n\n".join([self.dialogs[x].to_markdown() for x in self.dialogs])
        res = res.strip()
        return res

    @classmethod
    def from_markdown(cls, markdown: str):
        # Parse a string with markdown and return an Story object
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
                # regular expression to find the next dialog id
                nextdialogid = re.search(r"- (.+):", line).group(1).strip()
                # regular expression to find the choice text
                choicetext = re.search(r": (.+)", line).group(1).strip()
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
        self.G = nx.DiGraph()
        for dialogid in self.dialogs:
            self.G.add_node(dialogid)
            for choiceid in self.dialogs[dialogid].choices:
                self.G.add_edge(dialogid, choiceid)

    @requires(matplotlib_req, networkx_req)
    def plot_graph(self, graphfname: str = None):
        self.create_graph()
        nx.draw(self.G, with_labels=True)
        if graphfname is not None:
            plt.savefig(graphfname)
        else:
            plt.show()

    @requires(networkx_req)
    def has_subgraphs(self):
        self.create_graph()
        # check if there are subgraphs (i.e. multiple stories)
        return nx.number_weakly_connected_components(self.G) > 1

    def check_integrity(self):
        if _graph and self.has_subgraphs():
            return False
        # check if all the choices are valid
        for dialogid in self.dialogs:
            for choiceid in self.dialogs[dialogid].choices:
                if choiceid not in self.dialogs:
                    return False
        return True

    def prune_dangling_choices(self):
        # remove choices that point to a dialog that does not exist
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
