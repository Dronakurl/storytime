"""A textual app for storytime_ai."""
import re
import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import ClassVar, Iterable

from textual import events, work
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import (Button, DataTable, DirectoryTree, Footer, Header,
                             Input, Label, ListItem, ListView, Markdown,
                             RichLog, Static)
from textual.worker import WorkerState

from storytime_ai.choice import Choice
from storytime_ai.mylog import get_log
from storytime_ai.story import Story, _openai
from storytime_ai.utils import getfilelist

log = get_log("st")


class TextLogMessage(Message):
    """A message to write to the text log."""

    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__()


class Prompt(Markdown):
    """A widget to display the current dialog text."""

    prompt = reactive("Prompt")

    async def watch_prompt(self, prompt):
        # await self.clear()
        self.update(prompt)


class Choices(ListView):
    BINDINGS = [
        Binding("j", "cursor_down", "Cursor Down", show=False),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("l", "select_cursor", "Select", show=False),
    ]
    choices = reactive(dict(choice1=Choice("Choice 1", "initial")))
    choicestr = reactive("")

    def watch_choices(self, choices):
        self.clear()
        print(choices)
        for nextdialogid, content in choices.items():
            self.append(
                ListItem(
                    Markdown(("**" + content.nextdialogid + "**: " + content.text).strip()),
                    id="choice" + nextdialogid,
                )
            )

    def watch_choicestr(self, choicestr):
        print(choicestr)
        self.watch_choices(self.choices)


class MyHeader(Static):
    """A custom header."""

    title = reactive("Storyteller")
    stats = reactive("Stats")

    def compose(self):
        yield Horizontal(
            Label("Storyteller", id="headertitle"),
            Label("Stats", id="headerstats"),
        )

    def watch_title(self, title):
        self.query_one("#headertitle").update(title)

    def watch_stats(self, stats):
        self.query_one("#headerstats").update(stats)


class StoryInterface(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("m", "menu_screen", "Menu"),
        ("p", "properties_screen", "Properties"),
        ("a", "add_choice", "Add Choice"),
        # *([("g", "generate_screen", "Generate")] if _openai else []),
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
        yield MyHeader(id="header")
        yield Horizontal(
            Vertical(
                Prompt(id="text"),
                Choices(id="choices"),
            ),
            RichLog(highlight=True, markup=True, wrap=True, id="log"),
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """The next dialog is selected."""
        nextdialogid = event.item.id[6:]
        self.post_message(TextLogMessage(f"Selected: {nextdialogid}"))
        self.upd_text(nextdialogid)

    @work(exclusive=True)
    async def upd_text(self, nextdialogid: str) -> None:
        async for currentresult, _ in self.app.story.continue_story(nextdialogid, override_existing=False):
            self.query_one("#text").update(currentresult)
        self.display_currentdialog()

    def on_mount(self) -> None:
        fileprovided = False
        if len(sys.argv) > 1:
            fname = Path(sys.argv[1])
            fileprovided = True
        else:
            fname = Path(str(files("storytime_ai.templates").joinpath("story.md")))
        self.load_story(fname)
        if fileprovided:
            self.app.push_screen("Story")

    def action_back(self):
        """Go back to the previous dialog."""
        self.app.story.back_dialog()
        self.display_currentdialog()

    def action_load_screen(self):
        self.app.push_screen("Load")

    def action_save_screen(self):
        self.app.push_screen("Save")

    def action_menu_screen(self):
        self.app.push_screen("Start")

    def action_properties_screen(self):
        self.app.push_screen("Properties")

    def action_generate_screen(self):
        self.app.push_screen("Generate")

    def action_add_choice(self):
        self.app.push_screen("Add Choice")
        self.app.SCREENS["Add Choice"].query_one("#prompt").value = ""

    def action_toggle_log(self):
        if self.query_one("#log").styles.display == "none":
            self.query_one("#log").styles.display = "block"
        else:
            self.query_one("#log").styles.display = "none"

    def load_story(self, fname: Path):
        """Load the story from a file."""
        if not fname.is_file():
            raise FileNotFoundError
        self.app.story = Story.from_markdown_file(fname)
        self.post_message(TextLogMessage(f"Loaded Title: \n {self.app.story.title} from {fname}"))
        if not self.app.story.check_integrity() and not _openai:
            errors = self.app.story.prune_dangling_choices()
            self.post_message(TextLogMessage("Pruned dangling choices: \n" + "\n".join(errors)))
        self.display_currentdialog()
        self.set_focus(self.query_one("#choices"))
        self.app.title = self.app.story.title
        self.query_one("#header").stats = f"{len(self.app.story.dialogs)} dialogues"

    def display_currentdialog(self):
        """Update reactive variables, so current dialog is displayed."""
        # Update the text.
        text = "## " + self.app.story.currentdialog.dialogid + "\n\n" + self.app.story.currentdialog.text
        md = self.query_one("Prompt")
        md.prompt = text
        # Update the choices.
        self.query_one(Choices).choices = self.app.story.currentdialog.choices
        self.query_one(Choices).choicestr = self.app.story.currentdialog.choices_to_markdown()


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


@dataclass
class StoryItem:
    """A story item for the list view."""

    title: str
    filename: str
    stats: str
    fullpath: Path


class StoryListItem(ListItem):
    contents = reactive(
        StoryItem(
            title="The Story",
            filename="story.md",
            stats="0 dialogs",
            fullpath=Path("story.md"),
        )
    )

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("The Story", classes="storylisttitle"),
            Horizontal(
                Label("story.md", classes="storylistfilename"),
                Label("0 dialogues", classes="storyliststats"),
            ),
        )

    def watch_contents(self, contents):
        self.query_one(".storylisttitle").update(contents.title)
        self.query_one(".storylistfilename").update(contents.filename)
        self.query_one(".storyliststats").update(contents.stats)

    def watch_highlighted(self, highlighted):
        if highlighted:
            self.set_classes("storylistitemhighlighted")
        else:
            self.set_classes("storylistitem")


class ListStories(ListView):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("j", "cursor_down", "Cursor Down", show=False),
        Binding("l", "select_cursor", "Select", show=False),
    ]

    stories = reactive(
        [
            StoryItem(
                title="The Story",
                filename="story.md",
                stats="0 dialogues",
                fullpath=Path("story.md"),
            )
        ]
    )

    async def watch_stories(self, stories):
        await self.clear()
        for story in stories:
            listitem = StoryListItem()
            await self.append(listitem)
            listitem.contents = story

    def on_mount(self) -> None:
        storyfiles = getfilelist("./", "md", withpath=True)
        stories = [
            Story.from_markdown_file(fname=f)
            for f in storyfiles
            if (f.name if isinstance(f, Path) else f) != "README.md"
        ]
        storyitems = [
            StoryItem(
                title=s.title,
                filename=Path(s.markdown_file).name,
                stats=f"{len(s.dialogs)} dialogues",
                fullpath=Path(s.markdown_file),
            )
            for s in stories
        ]
        self.stories = storyitems


class LoadScreen(ModalScreen):
    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "quit", "Quit"),
        ("c", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Vertical(
            Label("Load story", classes="titlelabel"),
            ListStories(id="storylist"),
            FilteredDirectoryTree("./", id="directorytree"),
            Button("Pick file from directory", id="pickfile"),
            classes="loadcontainer",
        )
        yield Footer()

    def action_cancel(self):
        self.app.pop_screen()

    def on_mount(self) -> None:
        self.set_focus(self.query_one("#storylist"))
        self.query_one("#directorytree").styles.display = "none"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.log("button pressed")
        self.log(event.button.id)
        self.log(self.query_one("#pickfile").label)
        if event.button.id != "pickfile":
            return
        if str(self.query_one("#pickfile").label) == "Pick file from directory":
            self.query_one("#pickfile").label = "Pick file from list"
            self.query_one("#directorytree").styles.display = "block"
            self.query_one("#storylist").styles.display = "none"
            self.set_focus(self.query_one("#directorytree"))
        else:
            self.query_one("#pickfile").label = "Pick file from directory"
            self.query_one("#directorytree").styles.display = "none"
            self.query_one("#storylist").styles.display = "block"
            self.set_focus(self.query_one("#storylist"))

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.app.push_screen("Story")
        self.app.screen.load_story(Path(event.path))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.app.push_screen("Story")
        self.app.screen.load_story(Path(event.item.contents.fullpath))


class GenerateOut(RichLog):
    gptout = reactive("Output will appear here")

    def watch_gptout(self, gptout):
        self.clear()
        self.write(gptout)

    def __init__(self, **kwargs):
        super().__init__(wrap=True, markup=True, **kwargs)


class GenerateScreen(ModalScreen):
    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "quit", "Quit"),
        ("m", "menu", "Menu"),
        ("c", "cancel", "Cancel"),
        ("s", "save", "Save story"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Create story", classes="titlelabel"),
            Input("", id="prompt", placeholder="Enter a story idea and press ENTER"),
            Horizontal(
                Button("Cancel generation", id="cancel"),
                Button("Play the story", id="usestory"),
                classes="buttoncontainer",
            ),
            GenerateOut(id="gptout"),
            classes="generatecontainer",
        )
        yield Footer()

    def action_menu(self):
        self.app.push_screen("Start")

    def action_cancel(self):
        self.app.push_screen("Story")

    def action_save(self):
        self.app.push_screen("Save")

    def on_mount(self) -> None:
        self.set_focus(self.query_one("#prompt"))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Avoid that the story generation is just restarted every time the user presses enter
        for w in self.app.workers:
            if w.name == "upd_gptout" and w.state == WorkerState.RUNNING:
                return
        self.post_message(TextLogMessage(f"Input: {event.value}"))
        self.upd_gptout(prompt=event.value)

    @work(exclusive=True)
    async def upd_gptout(self, prompt: str = "A story about a pirate") -> None:
        # sg = StoryGenerator(prompt=prompt)
        async for cur, _ in self.app.story.generate_story(prompt=prompt):
            # async for cur, _ in self.app.story.generate_story_from_file(fname="./storytime_ai/templates/minimal.md"):
            self.query_one("#gptout").gptout = cur

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.post_message(TextLogMessage(f"Button pressed: {event.button.id}"))
        if event.button.id == "cancel":
            # Cancel the story generation
            for w in self.app.workers:
                if w.name == "upd_gptout" and w.state == WorkerState.RUNNING:
                    w.cancel()
        elif event.button.id == "usestory":
            self.post_message(TextLogMessage("Using story"))
            st = Story.from_markdown(self.query_one("#gptout").gptout)
            st.markdown_file = Path("/tmp/story.md")
            st.save_markdown()
            self.app.SCREENS["Story"].load_story(st.markdown_file)
            self.app.push_screen("Story")


class AddChoiceScreen(ModalScreen):
    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "quit", "Quit"),
        ("m", "menu", "Menu"),
        ("c", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Next dialog", classes="titlelabel"),
            Input("", id="prompt", placeholder="Enter a next choice (header: description) and press ENTER"),
            classes="addchoicecontainer",
        )
        yield Footer()

    def action_menu(self):
        self.app.push_screen("Start")

    def action_cancel(self):
        self.app.push_screen("Story")

    def action_save(self):
        self.app.push_screen("Save")

    def on_mount(self) -> None:
        self.set_focus(self.query_one("#prompt"))

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.app.push_screen("Story")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        x = re.search(r"(.+): (.+)", event.value)
        if not x:
            text = description = event.value
        else:
            description, text = x.groups()
        self.app.story.addchoice(text, description)
        self.app.SCREENS["Story"].display_currentdialog()
        self.app.push_screen("Story")


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
                self.post_message(TextLogMessage("Please enter a filename"))
                return
            st = self.app.story
            st.markdown_file = Path(fname)
            st.save_markdown()
            self.post_message(TextLogMessage(f"Saved to {fname}"))
            self.query_one("#savefeedback").update(f"Saved to {fname}")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "savename":
            return

    def on_mount(self) -> None:
        self.set_focus(self.query_one("#savename"))

    def action_cancel(self):
        """Return to the story screen."""
        self.app.pop_screen()


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
        proptable = [(k, v) for k, v in self.app.story.properties.items()]
        if len(proptable) == 0:
            proptable = [("None", "None")]
        self.post_message(TextLogMessage(f"Properties: {proptable}"))
        table.add_rows(proptable)

    def action_cancel(self):
        """Return to the story screen."""
        self.app.push_screen("Story")


class MenuListView(ListView):
    BINDINGS = [
        Binding("j", "cursor_down", "Cursor Down", show=False),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("l", "select_cursor", "Select", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield ListItem(Label("Load story"), id="menu_load")
        yield ListItem(Label("Generate story"), id="menu_generate")
        yield ListItem(Label("View current story"), id="menu_current")
        yield ListItem(Label("Save current story"), id="menu_save")
        yield ListItem(Label("Quit"), id="menu_quit")


class StartScreen(Screen):
    """The start screen of the app."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        Binding("m", "cancel", "Cancel", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Storytime", classes="titlelabel"),
            MenuListView(id="menu"),
            id="startcontainer",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.set_focus(self.query_one("#menu"))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.log(f"Selected: {event.item.id}")
        if event.item.id == "menu_load":
            self.app.push_screen("Load")
        elif event.item.id == "menu_generate":
            self.app.push_screen("Generate")
        elif event.item.id == "menu_current":
            self.app.push_screen("Story")
        elif event.item.id == "menu_save":
            self.app.push_screen("Save")
        elif event.item.id == "menu_quit":
            self.app.exit()

    def action_cancel(self):
        self.app.pop_screen()


class Storytime(App):
    SCREENS = {
        "Start": StartScreen(),
        "Story": StoryInterface(),
        "Load": LoadScreen(),
        "Save": SaveScreen(),
        "Properties": PropertiesScreen(),
        "Generate": GenerateScreen(),
        "Add Choice": AddChoiceScreen(),
    }
    CSS_PATH = "templates/app.css"

    def on_mount(self) -> None:
        """Start all Screens"""
        self.push_screen("Load")
        self.push_screen("Add Choice")
        self.push_screen("Save")
        self.push_screen("Generate")
        self.push_screen("Story")
        self.push_screen("Start")

    # The custom TextLogMessage event is handled here.
    def on_text_log_message(self, event: TextLogMessage):
        log = self.SCREENS["Story"].query_one("#log", expect_type=RichLog)  # type:ignore
        log.wrap = True
        log.write(event.text)

    def watch_title(self, title):
        try:
            self.SCREENS["Story"].query_one("#header").title = title
        except NoMatches:
            pass


def startapp():
    if not _openai:
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


if __name__ == "__main__":
    # if not __debug__:
    #     print("WARNING: Running in debug mode with back button and log")
    #     print("Start without -O to disable debug mode")
    #     input("Press enter to continue")
    startapp()
