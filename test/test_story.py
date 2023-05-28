from story import Dialog, Choice, Story
import pytest
import os


def test_choice():
    choice = Choice("First line with Ü\nSecond line with #", "Next Dialogue ID")
    assert choice.to_Markdown() == "- Next Dialogue ID: First line with Ü\nSecond line with #"


def test_dialog():
    dialog = Dialog(
        "Coole IDß",
        "Text in Unicode\n\n# Heading",
        {
            "eins": Choice("zweiter text", "eins"),
            "zwei": Choice("dritter text", "zwei"),
        },
        "PROPERTY test = 1",
    )
    assert (
        dialog.to_Markdown()
        == """## Coole IDß
LOGIC PROPERTY test = 1

Text in Unicode

# Heading
- eins: zweiter text

- zwei: dritter text"""
    )


def get_test_story():
    return Story(
        {
            "Coole IDß": Dialog(
                "Coole IDß",
                "Text in Unicode\n\n# Heading",
                {
                    "eins": Choice("zweiter text", "eins"),
                    "zwei": Choice("dritter text", "zwei"),
                },
                "PROPERTY 'test' = 1"
                + os.linesep
                + "PROPERTY 'test2' = 'test' + 1"
                + os.linesep
                + "PROPERTY 'test3' = self.story.title:='adsd'",
            ),
            "eins": Dialog(
                "eins",
                "zweiter text",
                {
                    "drei": Choice("vierter text", "drei"),
                },
                "NEXTDIALOG 'zwei' IF 'test' == 1",
            ),
            "zwei": Dialog("zwei", "dritter text", {}),
        },
        "My Story",
    )


def test_next_dialog():
    story = get_test_story()
    story.next_dialog("zwei")
    assert story.currentdialog == story.dialogs["zwei"]


def test_property_logic():
    story = get_test_story()
    assert story.properties["test"] == 1
    assert story.properties["test2"] == 2


def test_next_dialog_logic():
    story = get_test_story()
    story.next_dialog("eins")
    # assert list(story.currentdialog.choices.keys())[0] == "zwei"
    assert story.currentdialog == story.dialogs["zwei"]


def test_back_dialog():
    story = get_test_story()
    story.properties["test"] = 2
    story.next_dialog("eins")
    story.next_dialog("zwei")
    assert len(story.prevdialogids) == 3
    story.back_dialog()
    assert len(story.prevdialogids) == 2
    assert story.currentdialog == story.dialogs["eins"]
    story.back_dialog()
    assert story.currentdialog == story.dialogs["Coole IDß"]
    story.back_dialog()
    assert story.currentdialog == story.dialogs["Coole IDß"]


def test_property_logic_minimal():
    story = Story.from_markdown_file("./data/minimal.md")
    assert story.properties["Health Points"] == 100
    story.next_dialog("Go left")
    assert story.properties["Health Points"] == 90
    story.next_dialog("Turn to the castle")
    assert story.currentdialog == story.dialogs["Injured"]


@pytest.mark.parametrize(
    "file",
    [
        "./data/story.md",
        "./data/minimal.md",
        "./data/broken.md",
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
