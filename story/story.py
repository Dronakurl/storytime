import json
from pathlib import Path
import re

class Choice:
    def __init__(self, text: str, nextdialogid: str):
        self.nextdialogid = nextdialogid
        self.text = text

    def __repr__(self):
        return f"Choice({self.text}, {self.nextdialogid})"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["text"], data["nextdialogid"])

    @classmethod
    def dict_from_dict(cls, data: dict):
        return {x: cls.from_dict(data[x]) for x in data}

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def to_Markdown(self):
        return f"- {self.nextdialogid}: {self.text}"

    def __eq__(self, other):
        return self.toJson() == other.toJson()


class Dialog:
    def __init__(self, dialogid: str, text: str, choices: dict[str, Choice]):
        self.dialogid = dialogid
        self.text = text
        self.choices = choices

    def __repr__(self):
        return f"Dialog({self.dialogid}, {self.text}, {self.choices})"

    @classmethod
    def from_dict(cls, dialogid: str, data: dict):
        return cls(dialogid, data["text"], Choice.dict_from_dict(data["choices"]))

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def choices_to_Markdown(self):
        return "\n\n".join([self.choices[x].to_Markdown() for x in self.choices])

    def to_Markdown(self):
        return f"## {self.dialogid}\n{self.text}\n{self.choices_to_Markdown()}"

    def __eq__(self, other):
        return self.toJson() == other.toJson()


class PathWithDict(Path):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __dict__(self):
        return {"path": self.__str__()}


class Story:
    def __init__(self, dialogs: dict[str, Dialog], title: str = "Story", state: dict = {}):
        self.dialogs = dialogs
        self.currentdialog = self.dialogs[list(dialogs.keys())[0]]
        self.prevdialogids = [list(dialogs.keys())[0]]
        self.title = title
        self.state = state
        self.markdown_file = PathWithDict("story.md")

    @classmethod
    def from_dict(cls, data: dict, title: str = "Story"):
        x = {x: Dialog.from_dict(x, data[x]) for x in data}
        return cls(x, title=title)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def to_Markdown(self):
        res = f"# {self.title}\n\n"
        res += "\n\n".join([self.dialogs[x].to_Markdown() for x in self.dialogs])
        res = res.strip()
        return res

    def __repr__(self):
        return self.toJson()

    def __eq__(self, other):
        return self.toJson() == other.toJson()

    def save_markdown(self):
        with open(self.markdown_file, "w") as f:
            f.write(self.to_Markdown())

    def next_dialog(self, nextdialogid: str):
        self.prevdialogids.append(self.currentdialog.dialogid)
        self.currentdialog = self.dialogs[nextdialogid]

    def back_dialog(self):
        print(self.prevdialogids)
        if len(self.prevdialogids) > 1:
            prvdiag = self.prevdialogids.pop()
        else:
            prvdiag = self.prevdialogids[0]
        self.currentdialog = self.dialogs[prvdiag]

    # class method that creates a story from a markdown string created with the to_Markdown method
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
                    dialogs[dialogid] = Dialog(dialogid, text, choices)
                    text = ""
                    choices = {}
                    nextdialogid = ""
                dialogid = line[3:].strip()
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
        choices[nextdialogid] = Choice(choicetext, nextdialogid)
        dialogs[dialogid] = Dialog(dialogid, text, choices)
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
            res.markdown_file = fname
            return res
