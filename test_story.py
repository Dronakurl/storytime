import json
from story import Dialog, Choice, Story

def test_choice():
    data = {
        "1": {"text": "zweiter text", "nextdialogid": "eins"},
        "2": {"text": "dritter text", "nextdialogid": "zwei"},
    }
    choices = Choice.dict_from_dict(data)
    assert choices["1"] == Choice.from_dict("1", json.loads(choices["1"].toJson()))


def test_dialog():
    data = {
        "text": "erster text",
        "choices": {
            "1": {"text": "zweiter text", "nextdialogid": "eins"},
            "2": {"text": "dritter text", "nextdialogid": "zwei"},
        },
    }
    dialog = Dialog.from_dict("initial", data)
    assert dialog == Dialog.from_dict("initial", json.loads(dialog.toJson()))


tstdict = {
    "initial": {
        "text": "erster text",
        "choices": {
            "1": {"text": "zweiter text", "nextdialogid": "eins"},
            "2": {"text": "dritter text", "nextdialogid": "zwei"},
        },
    },
    "eins": {
        "text": "vierter text",
        "choices": {"1": {"text": "fünfter text", "nextdialogid": "zwei"}},
    },
    "zwei": {
        "text": "sechster text",
        "choices": {"1": {"text": "siebter text", "nextdialogid": "eins"}},
    },
}

def test_story():
    story = Story.from_dict(tstdict)
    astor = Story.from_dict(json.loads(story.toJson())["dialogs"])
    assert story == astor

def test_next_dialog():
    story = Story.from_dict(tstdict)
    story.next_dialog("1")
    assert story.currentdialog == story.dialogs["eins"]
    story.next_dialog("1")
    assert story.currentdialog == story.dialogs["zwei"]

def test_toMarkdown():
    story = Story.from_dict(tstdict)
    print(story.toMarkdown())

