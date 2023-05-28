"""
This module contains the classes that represent a story.
A Story is a collection of Dialogs.
A Dialog contains a selection of Choices.
"""
from pathlib import Path
import re


class Choice:
    def __init__(self, text: str, nextdialogid: str):
        self.nextdialogid = nextdialogid
        self.text = text

    def __repr__(self):
        return f"Choice({self.text}, {self.nextdialogid})"

    def to_Markdown(self):
        return f"- {self.nextdialogid}: {self.text}"

    def __eq__(self, other):
        return self.to_Markdown() == other.to_Markdown()


class Dialog:
    def __init__(self, dialogid: str, text: str, choices: dict[str, Choice], logic: str = ""):
        self.dialogid = dialogid
        self.text = text
        self.choices = choices
        self.logic = logic

    def addchoice(self, text: str, nextdialogid: str):
        choice = Choice(text, nextdialogid)
        self.choices[choice.nextdialogid] = choice

    def __repr__(self):
        return f"Dialog({self.dialogid}, {self.text}, {self.choices})"

    def choices_to_Markdown(self):
        return "\n\n".join([self.choices[x].to_Markdown() for x in self.choices])

    def write_logic(self):
        # each line is prefixed with "LOGIC: "
        if self.logic.strip() == "":
            return ""
        return "\n".join([f"LOGIC {x}" for x in self.logic.split("\n")]) + "\n\n"

    def to_Markdown(self):
        return f"## {self.dialogid}\n{self.write_logic()}{self.text}\n{self.choices_to_Markdown()}"

    def __eq__(self, other):
        return self.to_Markdown() == other.to_Markdown()


class Story:
    def __init__(self, dialogs: dict[str, Dialog], title: str = "Story"):
        self.dialogs = dialogs
        self.currentdialog = self.dialogs[list(dialogs.keys())[0]]
        self.prevdialogids = [list(dialogs.keys())[0]]
        self.title = title
        self.markdown_file = "story.md"
        self.properties = {}
        self.exec_logic()

    def to_Markdown(self):
        res = f"# {self.title}\n\n"
        res += "\n\n".join([self.dialogs[x].to_Markdown() for x in self.dialogs])
        res = res.strip()
        return res

    def __repr__(self):
        return self.to_Markdown()

    def __eq__(self, other):
        return self.to_Markdown() == other.to_Markdown()

    def save_markdown(self, fname: str = None):
        if fname is not None:
            self.markdown_file = fname
        with open(Path(self.markdown_file), "w") as f:
            f.write(self.to_Markdown())

    def next_dialog(self, nextdialogid: str):
        self.prevdialogids.append(self.currentdialog.dialogid)
        self.currentdialog = self.dialogs[nextdialogid]
        logmsg = self.currentdialog.logic
        self.exec_logic()
        return logmsg

    def addchoice(self, text: str, nextdialogid: str):
        self.currentdialog.addchoice(text, nextdialogid)

    def back_dialog(self):
        print(self.prevdialogids)
        if len(self.prevdialogids) > 1:
            prvdiag = self.prevdialogids.pop()
        else:
            prvdiag = self.prevdialogids[0]
        self.currentdialog = self.dialogs[prvdiag]

    def check_integrity(self):
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

    def exec_logic_old(self):
        if len(self.currentdialog.logic) <= 1:
            return
        try:
            exec(self.currentdialog.logic)
        except Exception as e:
            print(f"Error {e} in logic {self.currentdialog.logic}")

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
                    if eval(cond, {"__builtins__": None}, {"properties": self.properties}):
                        self.currentdialog.choices = {x.group(1): Choice("Continue", x.group(1))}
                except Exception as e:
                    print(f"Error {e} in logic {strl}")

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
