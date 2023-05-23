import json
from story import Dialog, Choice, Story
import pytest
import os


def test_choice():
    data = {
        "eins": {"text": "zweiter text", "nextdialogid": "eins"},
        "zwei": {"text": "dritter text", "nextdialogid": "zwei"},
    }
    choices = Choice.dict_from_dict(data)
    assert choices["eins"] == Choice.from_dict(json.loads(choices["eins"].toJson()))


def test_dialog():
    data = {
        "text": "erster text",
        "choices": {
            "eins": {"text": "zweiter text", "nextdialogid": "eins"},
            "zwei": {"text": "dritter text", "nextdialogid": "zwei"},
        },
    }
    dialog = Dialog.from_dict("initial", data)
    assert dialog == Dialog.from_dict("initial", json.loads(dialog.toJson()))


tstdict = {
    "initial": {
        "text": "erster text",
        "choices": {
            "eins": {"text": "zweiter text", "nextdialogid": "eins"},
            "zwei": {"text": "dritter text", "nextdialogid": "zwei"},
        },
    },
    "eins": {
        "text": "vierter text",
        "choices": {"zwei": {"text": "fünfter text", "nextdialogid": "zwei"}},
    },
    "zwei": {
        "text": "sechster text",
        "choices": {"eins": {"text": "siebter text", "nextdialogid": "eins"}},
    },
}


def test_story():
    story = Story.from_dict(tstdict)
    astor = Story.from_dict(json.loads(story.toJson())["dialogs"])
    assert story == astor


def test_next_dialog():
    story = Story.from_dict(tstdict)
    story.next_dialog("eins")
    assert story.currentdialog == story.dialogs["eins"]
    story.next_dialog("zwei")
    assert story.currentdialog == story.dialogs["zwei"]


def test_to_Markdown():
    story = Story.from_dict(tstdict)
    print(story.to_Markdown())


def test_back_dialog():
    story = Story.from_dict(tstdict)
    story.next_dialog("eins")
    story.next_dialog("zwei")
    assert len(story.prevdialogids) == 3
    story.back_dialog()
    assert len(story.prevdialogids) == 2
    assert story.currentdialog == story.dialogs["eins"]
    story.back_dialog()
    assert story.currentdialog == story.dialogs["initial"]
    story.back_dialog()
    assert story.currentdialog == story.dialogs["initial"]


def test_from_markdown():
    story = Story.from_dict(tstdict)
    markdown = story.to_Markdown()
    print(markdown)
    storycmp = Story.from_markdown(markdown)
    print(storycmp)


@pytest.mark.parametrize(
    "file",
    [
        "./data/story.md",
        "./data/story_with_properties.md",
        "./data/minimal2.md",
    ],
)
def test_from_markdown_file(file):
    story = Story.from_markdown_file(file)
    with open(file) as f:
        md = f.read().strip()
    md = os.linesep.join([s for s in md.splitlines() if s])
    sm = story.to_Markdown()
    sm = os.linesep.join([s for s in sm.splitlines() if s])
    assert md == sm
    print(story.to_Markdown())


def test_addchoice():
    story = Story.from_markdown_file("./data/story.md")
    story.addchoice("new text", "eins")
    assert story.currentdialog.choices["eins"].nextdialogid == "eins"
    assert story.currentdialog.choices["eins"].text == "new text"


def test_integrity():
    story = Story.from_markdown_file("./data/story.md")
    assert story.check_integrity()
    story.addchoice("new text", "eins")
    assert not story.check_integrity()
    story.prune_dangling_choices()
    assert story.check_integrity()


test_from_markdown_file("./data/minimal2.md")
