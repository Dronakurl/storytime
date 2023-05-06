import json
from story import Dialog, Choice, Story

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

def test_from_markdown_file():
    story=Story.from_markdown_file("./data/story.md")
    with open("./data/story.md","r") as f:
        md=f.read().strip()
    # assert md==story.to_Markdown()
    print(story.to_Markdown())

# test_from_markdown()
test_from_markdown_file()


