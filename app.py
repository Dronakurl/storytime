from pathlib import Path
import sys
from typing import Iterable

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header
from textual.widgets import (
    DirectoryTree,
    Footer,
    ListItem,
    ListView,
    Markdown,
    TextLog,
)

from story import Choice, Story


class TextLogMessage(Message):
    """A message to write to the text log."""

    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__()


class Prompt(Markdown):
    prompt = reactive("Prompt")

    def watch_prompt(self, prompt):
        self.update(prompt)


class Choices(ListView):
    BINDINGS = [
        Binding("j", "cursor_down", "Cursor Down", show=False),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("l", "select_cursor", "Select", show=False),
    ]
    choices = reactive(dict(choice1=Choice("Choice 1", "initial")))

    async def watch_choices(self, choices):
        """Update the choices."""
        await self.clear()
        self.log(choices)
        for nextdialogid, content in choices.items():
            self.append(
                ListItem(
                    Markdown(("**" + content.nextdialogid + "**: " + content.text).strip()),
                    id="choice" + nextdialogid,
                )
            )


class StoryInterface(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        Binding("c", "focus('choices')", "Choices", show=False),
        ("s", "load_screen", "Settings"),
        ("h", "back", "Back"),
        ("t", "toggle_log", "Toggle Log"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        # yield Dialog()
        yield Container(
            Prompt(id="text"),
            TextLog(highlight=True, markup=True, wrap=True),
            Container(Choices(id="choices"), id="choicecontainer"),
            id="layout",
        )
        yield Footer()

    def on_key(self, event: events.Key) -> None:
        pass

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.post_message(TextLogMessage(f"Selected: {event.item.id[6:]}"))
        logmsg = self.story.next_dialog(event.item.id[6:])
        self.post_message(TextLogMessage(f"Logic: {logmsg}"))
        self.display_currentdialog()

    def on_mount(self) -> None:
        if len(sys.argv) > 1:
            fname = Path(sys.argv[1])
        else:
            fname = Path("./data/story.md")
        self.load_story(fname)

    def action_back(self):
        """Go back to the previous dialog."""
        self.story.back_dialog()
        self.display_currentdialog()

    def action_load_screen(self):
        """Load the load screen."""
        app.switch_screen("Load")

    def action_toggle_log(self):
        """Toggle the log."""
        if self.query_one(TextLog).styles.display == "none":
            self.query_one(TextLog).styles.display = "block"
            self.query_one("#text").styles.column_span = 2
            self.query_one("#choicecontainer").styles.column_span = 2
        else:
            self.query_one(TextLog).styles.display = "none"
            self.query_one("#text").styles.column_span = 3
            self.query_one("#choicecontainer").styles.column_span = 3

    def load_story(self, fname: Path):
        """Load the story from a file."""
        if not fname.is_file():
            raise FileNotFoundError
        self.story = Story.from_markdown_file(fname)
        self.post_message(TextLogMessage(f"Loaded Title: {self.story.title} from {fname}"))
        if not self.story.check_integrity():
            errors = self.story.prune_dangling_choices()
            self.post_message(TextLogMessage("Pruned dangling choices: \n" + "\n".join(errors)))
        self.display_currentdialog()
        self.set_focus(self.query_one("#choices"))
        self.app.title = self.story.title

    def display_currentdialog(self):
        """Update reactive variables, so current dialog is displayed."""
        """ Update the text. """
        text = "# " + self.story.currentdialog.dialogid + "\n\n" + self.story.currentdialog.text
        md = self.query_one("Prompt")
        md.prompt = text
        """ Update the choices. """
        self.query_one(Choices).choices = self.story.currentdialog.choices


class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            path
            for path in paths
            if (
                not path.name.startswith(".")
                and (path.is_dir() or str(path).endswith(".md"))
                and path.name != "README.md"
            )
        ]


class SettingsScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield FilteredDirectoryTree("./")
        yield Footer()

    def action_cancel(self):
        """Return to the story screen."""
        app.push_screen("Story")

    def on_mount(self) -> None:
        self.set_focus(self.query_one("FilteredDirectoryTree"))


class Storytime(App):
    SCREENS = {"Story": StoryInterface(), "Load": SettingsScreen()}
    CSS_PATH = "./assets/app.css"

    def on_mount(self) -> None:
        self.push_screen("Story")
        self.push_screen("Load")
        self.switch_screen("Story")

    # The app must handle events to pass them to other screens.
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.push_screen("Story")
        self.screen.load_story(Path(event.path))

    # The custom TextLogMessage event is handled here.
    def on_text_log_message(self, event: TextLogMessage):
        self.query_one(TextLog).write(event.text)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = Path(sys.argv[1])
        if not fname.is_file():
            print(f"File not found. Exiting. Given filename: {fname}")
            sys.exit(1)
    app = Storytime()
    app.run()
