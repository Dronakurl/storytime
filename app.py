from pathlib import Path
import sys
from typing import Iterable, ClassVar
from threading import Thread

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, Vertical, Horizontal
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen, ModalScreen
from textual.widgets import Footer, Header, DataTable
from textual.widgets import (
    DirectoryTree,
    Footer,
    ListItem,
    ListView,
    Markdown,
    TextLog,
    Label,
    Static,
    Input,
    Button,
)

from story import Choice, Story
from gptstory import StoryGenerator, gptstory


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


class MyHeader(Static):
    """A custom header."""

    title = reactive("Storyteller")
    stats = reactive("Stats")

    def compose(self):
        yield Horizontal(Label("Storyteller", id="headertitle"), Label("Stats", id="headerstats"))

    def watch_title(self, title):
        self.query_one("#headertitle").update(title)

    def watch_stats(self, stats):
        self.query_one("#headerstats").update(stats)


class StoryInterface(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        Binding("c", "focus('choices')", "Choices", show=False),
        ("o", "load_screen", "Load Story"),
        ("s", "save_screen", "Save Story"),
        ("p", "properties_screen", "Properties"),
        *([("g", "generate_screen", "Generate")] if gptstory else []),
        *(
            [
                ("h", "back", "Back"),
                ("t", "toggle_log", "Toggle Log"),
            ]
            if not False
            else []
        ),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        # yield Header()
        yield MyHeader(id="header")
        yield Container(
            Prompt(id="text"),
            TextLog(highlight=True, markup=True, wrap=True, id="log"),
            Container(Choices(id="choices"), id="choicecontainer"),
            id="layout",
        )
        yield Footer()

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
        app.push_screen("Load")

    def action_save_screen(self):
        app.push_screen("Save")

    def action_properties_screen(self):
        app.push_screen("Properties")

    def action_generate_screen(self):
        app.push_screen("Generate")

    def action_toggle_log(self):
        if self.query_one("#log").styles.display == "none":
            self.query_one(TextLog).styles.display = "block"
            self.query_one("#text").styles.column_span = 2
            self.query_one("#choicecontainer").styles.column_span = 2
        else:
            self.query_one("#log").styles.display = "none"
            self.query_one("#text").styles.column_span = 3
            self.query_one("#choicecontainer").styles.column_span = 3

    def load_story(self, fname: Path):
        """Load the story from a file."""
        if not fname.is_file():
            raise FileNotFoundError
        self.story = Story.from_markdown_file(fname)
        self.post_message(TextLogMessage(f"Loaded Title: \n {self.story.title} from {fname}"))
        if not self.story.check_integrity():
            errors = self.story.prune_dangling_choices()
            self.post_message(TextLogMessage("Pruned dangling choices: \n" + "\n".join(errors)))
        self.display_currentdialog()
        self.set_focus(self.query_one("#choices"))
        self.app.title = self.story.title
        self.query_one("#header").stats = f"{len(self.story.dialogs)} dialogues"

    def display_currentdialog(self):
        """Update reactive variables, so current dialog is displayed."""
        """ Update the text. """
        text = "# " + self.story.currentdialog.dialogid + "\n\n" + self.story.currentdialog.text
        md = self.query_one("Prompt")
        md.prompt = text
        """ Update the choices. """
        self.query_one(Choices).choices = self.story.currentdialog.choices


class FilteredDirectoryTree(DirectoryTree):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("l", "toggle_node", "Toggle", show=False),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("j", "cursor_down", "Cursor Down", show=False),
    ]

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


class SettingsScreen(ModalScreen):
    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "quit", "Quit"),
        ("c", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Vertical(
            Label("Load story", classes="titlelabel"),
            FilteredDirectoryTree("./", id="directorytree"),
            classes="container",
        )
        yield Footer()

    def action_cancel(self):
        """Return to the story screen."""
        app.push_screen("Story")

    def on_mount(self) -> None:
        self.set_focus(self.query_one("FilteredDirectoryTree"))


class GenerateOut(TextLog):
    gptout = reactive("Output will appear here")

    def watch_gptout(self, gptout):
        self.clear()
        self.write(gptout)

    def __init__(self, **kwargs):
        super().__init__(wrap=True, markup=True, **kwargs)


class GenerateScreen(ModalScreen):
    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "quit", "Quit"),
        ("c", "cancel", "Cancel"),
        ("s", "save", "Save story"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Create story", classes="titlelabel"),
            Input("", id="prompt", placeholder="Enter a story idea and press ENTER"),
            Horizontal(
                Button("Play the story", id="usestory"),
                Button("Go back", id="cancel"),
                classes="buttoncontainer",
            ),
            GenerateOut(id="gptout"),
            classes="generatecontainer",
        )
        yield Footer()

    def action_cancel(self):
        app.push_screen("Story")

    def action_save(self):
        app.push_screen("Save")

    def on_mount(self) -> None:
        self.set_focus(self.query_one("#prompt"))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.post_message(TextLogMessage(f"Input: {event.value}"))
        self.counter_thread = Thread(target=self.upd_gptout, kwargs={"prompt": event.value})
        self.counter_thread.start()
        # self.upd_gptout(prompt=event.value)

    def upd_gptout(self, prompt: str = "Story output"):
        sg = StoryGenerator(prompt=prompt)
        for cur, _ in sg.generate_story():
            # for cur, chunk in sg.generate_story_from_file(fname="./data/chatgpttest.md"):
            self.query_one("#gptout").gptout = cur

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.post_message(TextLogMessage(f"Button pressed: {event.button.id}"))
        if event.button.id == "cancel":
            self.action_cancel()
        elif event.button.id == "usestory":
            self.post_message(TextLogMessage(f"Using story"))
            st = Story.from_markdown(self.query_one("#gptout").gptout)
            st.markdown_file = Path("/tmp/story.md")
            st.save_markdown()
            app.SCREENS["Story"].load_story(st.markdown_file)
            app.push_screen("Story")


class SaveScreen(ModalScreen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "cancel", "Cancel"),
        Binding("s", "cancel", "Cancel", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Save current story to file", classes="titlelabel"),
            Input("", id="savename", placeholder="Enter a filename"),
            Horizontal(
                Button("Save story to file", id="savestory"),
                Label("", id="savefeedback"),
                id="savebuttons",
            ),
            classes="savecontainer",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.post_message(TextLogMessage(f"Button pressed: {event.button.id}"))
        if event.button.id == "savestory":
            fname = self.query_one("#savename").value
            if fname == "":
                self.post_message(TextLogMessage(f"Please enter a filename"))
                return
            st = app.SCREENS["Story"].story
            st.markdown_file = Path(fname)
            st.save_markdown()
            self.post_message(TextLogMessage(f"Saved to {fname}"))
            self.query_one("#savefeedback").update(f"Saved to {fname}")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "savename":
            return

    def action_cancel(self):
        """Return to the story screen."""
        app.push_screen("Story")


class PropertiesTable(DataTable):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("j", "cursor_down", "Cursor Down", show=False),
        Binding("l", "cursor_right", "Cursor Right", show=False),
        Binding("h", "cursor_left", "Cursor Left", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(fixed_rows=1, show_cursor=False, **kwargs)


class PropertiesScreen(ModalScreen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "cancel", "Cancel"),
        Binding("p", "cancel", "Cancel", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Vertical(
            Label("Properties", classes="titlelabel"),
            PropertiesTable(id="propertytable"),
            classes="container",
        )
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#propertytable")
        table.add_columns("Property      ", "Value      ")
        self.on_screen_resume()

    def on_screen_resume(self) -> None:
        table = self.query_one("#propertytable")
        table.clear()
        proptable = [(k, v) for k, v in app.SCREENS["Story"].story.properties.items()]
        if len(proptable) == 0:
            proptable = [("None", "None")]
        self.post_message(TextLogMessage(f"Properties: {proptable}"))
        table.add_rows(proptable)

    def action_cancel(self):
        """Return to the story screen."""
        app.push_screen("Story")


class Storytime(App):
    SCREENS = {
        "Story": StoryInterface(id="storyscreen"),
        "Load": SettingsScreen(),
        "Save": SaveScreen(),
        "Properties": PropertiesScreen(),
        "Generate": GenerateScreen(),
    }
    CSS_PATH = "./assets/app.css"

    def on_mount(self) -> None:
        self.push_screen("Story")

    # The app must handle events to pass them to other screens.
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.push_screen("Story")
        self.screen.load_story(Path(event.path))

    # The custom TextLogMessage event is handled here.
    def on_text_log_message(self, event: TextLogMessage):
        log = self.SCREENS["Story"].query_one("#log", expect_type=TextLog)
        log.wrap = True
        log.write(event.text)

    def watch_title(self, title):
        try:
            self.SCREENS["Story"].query_one("#header").title = title
        except NoMatches:
            pass


if __name__ == "__main__":
    # if not __debug__:
    #     print("WARNING: Running in debug mode with back button and log")
    #     print("Start without -O to disable debug mode")
    #     input("Press enter to continue")
    if not gptstory:
        print("WARNING: GPT-Story not found. Running without GPT-Story")
        print("Set environment variable OPENAI_API_KEY to enable GPT-Story (in .env file)")
        input("Press enter to continue")
    if len(sys.argv) > 1:
        fname = Path(sys.argv[1])
        if not fname.is_file():
            print(f"File not found. Exiting. Given filename: {fname}")
            sys.exit(1)
    app = Storytime()
    app.run()
