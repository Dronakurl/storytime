from storytime_ai import Dialog, Choice, Story
import pytest
import os


def test_choice():
    choice = Choice("First line with Ü\nSecond line with #", "Next Dialogue ID")
    assert choice.to_markdown() == "- Next Dialogue ID: First line with Ü\nSecond line with #"


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
        dialog.to_markdown()
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
                + "PROPERTY 'test3' = (self.story.title:='adsd')",
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


def test_story_error(capsys):
    # test if errors in the logic are printed
    get_test_story()
    captured = capsys.readouterr()
    assert (
        captured.out.strip()
        == "Error cannot use assignment expressions with attribute (<string>, line 1) in logic PROPERTY 'test3' = (self.story.title:='adsd')".strip()
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
    story = Story.from_markdown_file("./storytime_ai/templates/minimal.md")
    assert story.properties["Health Points"] == 100
    story.next_dialog("Go left")
    assert story.properties["Health Points"] == 90
    story.next_dialog("Turn to the castle")
    assert story.currentdialog == story.dialogs["Injured"]


@pytest.mark.parametrize(
    "file",
    [
        "./storytime_ai/templates/story.md",
        "./storytime_ai/templates/minimal.md",
        "./storytime_ai/templates/minimal2.md",
        "./storytime_ai/templates/broken.md",
    ],
)
def test_from_markdown_file(file):
    """Compare only non-empty lines"""
    story = Story.from_markdown_file(file)
    with open(file) as f:
        md = f.read().strip()
    md = os.linesep.join([s.strip() for s in md.splitlines() if s])
    sm = story.to_markdown()
    sm = os.linesep.join([s.strip() for s in sm.splitlines() if s])
    assert md == sm


@pytest.mark.parametrize(
    "file",
    [
        "./storytime_ai/templates/story.md",
        "./storytime_ai/templates/minimal.md",
        "./storytime_ai/templates/minimal2.md",
    ],
)
def test_integrity_of_minimal(file):
    story = Story.from_markdown_file(file)
    assert story.check_integrity()


def test_addchoice():
    story = Story.from_markdown_file("./storytime_ai/templates/story.md")
    story.addchoice("new text", "eins")
    assert story.currentdialog.choices["eins"].nextdialogid == "eins"
    assert story.currentdialog.choices["eins"].text == "new text"


def test_integrity():
    story = Story.from_markdown_file("./storytime_ai/templates/story.md")
    assert story.check_integrity()
    story.addchoice("new text", "eins")
    assert not story.check_integrity()
    story.prune_dangling_choices()
    assert story.check_integrity()
