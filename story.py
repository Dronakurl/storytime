import json


class Choice:
    def __init__(self, choiceid: str, text: str, nextdialogid: str):
        self.choiceid = choiceid
        self.text = text
        self.nextdialogid = nextdialogid

    def __repr__(self):
        return f"Choice({self.choiceid}, {self.text}, {self.nextdialogid})"

    @classmethod
    def from_dict(cls, choiceid: str, data: dict):
        return cls(choiceid, data["text"], data["nextdialogid"])

    @classmethod
    def dict_from_dict(cls, data: dict):
        return {x: cls.from_dict(x, data[x]) for x in data}

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def toMarkdown(self):
        return f"- _{self.choiceid}_: {self.text}"

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

    def choices_toMarkdown(self):
        return "\n".join([self.choices[x].toMarkdown() for x in self.choices])

    def toMarkdown(self):
        return f"## {self.dialogid}\n{self.text}\n\n{self.choices_toMarkdown()}"

    def __eq__(self, other):
        return self.toJson() == other.toJson()


class Story:
    def __init__(self, dialogs: dict[str, Dialog]):
        self.dialogs = dialogs
        self.currentdialog = self.dialogs[list(dialogs.keys())[0]]

    @classmethod
    def from_dict(cls, data: dict):
        x = {x: Dialog.from_dict(x, data[x]) for x in data}
        return cls(x)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def toMarkdown(self):
        return "\n\n".join([self.dialogs[x].toMarkdown() for x in self.dialogs])

    def __repr__(self):
        return self.toJson()

    def __eq__(self, other):
        return self.toJson() == other.toJson()

    def next_dialog(self, choiceid: str):
        nextdialogid = self.currentdialog.choices[choiceid].nextdialogid
        self.currentdialog = self.dialogs[nextdialogid]



