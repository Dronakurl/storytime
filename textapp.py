import json
from story import Story, Dialog, Choice
from textual import events
from textual.reactive import reactive
from textual.containers import Container
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.widgets import ListView, ListItem, Label, Footer, Markdown, TextLog
from textual.binding import Binding, BindingType


class Prompt(Markdown):
    prompt = reactive("Prompt")

    def watch_prompt(self, prompt):
        self.update(prompt)


class Choices(ListView):
    BINDINGS=[
        Binding("j", "cursor_down", "Cursor Down", show=False),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("l", "select_cursor", "Select", show=False)
    ]
    choices = reactive(dict(choice1=Choice("choice1", "Choice 1", "initial")))

    async def watch_choices(self, choices):
        """Update the choices."""
        await self.clear()
        self.log(choices)
        for choiceid, content in choices.items():
            self.append(ListItem(Label(content.text), id="choice" + choiceid))


class Geschichte(App):
    BINDINGS = [("q", "quit", "Quit"), ("c", "focus('choices')", "Choices")]
    CSS_PATH = "list_view.css"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        # yield Dialog()
        yield Container(
            Prompt(id="text"),
            TextLog(highlight=True, markup=True),
            Container(Choices(id="choices"), id="choicecontainer"),
            id="layout",
        )

    def on_key(self, event: events.Key) -> None:
        pass

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        text_log = self.query_one(TextLog)
        curchoices=self.story.currentdialog.choices
        selectchoice=curchoices.get(event.item.id[6:])
        text_log.write(f"Selected: {selectchoice}\n")
        if selectchoice is None:
            raise ValueError("Choice not found")
        self.story.next_dialog(event.item.id[6:])
        self.display_currentdialog()

    def on_load(self) -> None:
        """Load the story from a file."""
        with open("story.json") as f:
            self.story = Story.from_dict(json.load(f))

    def on_mount(self) -> None:
        self.display_currentdialog()
        self.set_focus(self.query_one("#choices"))

    def display_currentdialog(self):
        """Display the current dialog."""
        text = self.story.currentdialog.text
        md = self.query_one("Prompt")
        md.prompt = text
        """ Update the choices. """
        self.query_one(Choices).choices = self.story.currentdialog.choices


if __name__ == "__main__":
    app = Geschichte()
    app.run()
