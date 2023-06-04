from .choice import Choice


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

    def choices_to_markdown(self):
        return "\n\n".join([self.choices[x].to_markdown() for x in self.choices])

    def write_logic(self):
        # each line is prefixed with "LOGIC: "
        if self.logic.strip() == "":
            return ""
        return "\n".join([f"LOGIC {x}" for x in self.logic.split("\n")]) + "\n\n"

    def to_markdown(self):
        return f"## {self.dialogid}\n{self.write_logic()}{self.text}\n{self.choices_to_markdown()}"

    def __eq__(self, other):
        return self.to_markdown() == other.to_markdown()
