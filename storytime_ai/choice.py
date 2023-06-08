class Choice:
    def __init__(self, text: str, nextdialogid: str):
        self.nextdialogid = nextdialogid
        self.text = text

    def __repr__(self):
        return f"Choice({self.text}, {self.nextdialogid})"

    def to_markdown(self):
        return f"- {self.nextdialogid}: {self.text}"

    def __eq__(self, other):
        return self.to_markdown() == other.to_markdown()
