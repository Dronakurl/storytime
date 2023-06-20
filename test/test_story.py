from storytime_ai import Dialog, Choice, Story
import pytest
import os


def assert_only_non_empty_lines(a, b):
    a = os.linesep.join([s.strip() for s in a.splitlines() if s])
    b = os.linesep.join([s.strip() for s in b.splitlines() if s])
    if a != b:
        print("a:")
        print(a)
        print("b:")
        print(b)
    assert a == b


def test_choice():
    choice = Choice("First line with Ü\nSecond line with #", "Next Dialogue ID")
    assert choice.to_markdown() == "- Next Dialogue ID: First line with Ü\nSecond line with #"


def get_test_dialog():
    return Dialog(
        "Coole IDß",
        "Text in Unicode\n\n### Heading",
        {
            "eins": Choice("zweiter text", "eins"),
            "zwei": Choice("dritter text", "zwei"),
        },
        "PROPERTY test = 1",
    )


def test_dialog():
    dialog = get_test_dialog()
    assert (
        dialog.to_markdown()
        == """## Coole IDß
LOGIC PROPERTY test = 1

Text in Unicode

### Heading
- eins: zweiter text

- zwei: dritter text"""
    )


def test_dialog_markdown_parser():
    dialog = get_test_dialog()
    dialog_parsed = Dialog.from_markdown(dialog.to_markdown())
    assert dialog_parsed == dialog


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
            "zwei": Dialog(
                "zwei",
                "dritter text",
                {},
            ),
        },
        "My Story",
    )


def get_simple_test_story():
    return Story(
        {
            "Coole ID": Dialog(
                "Coole ID",
                "Text",
                {
                    "eins": Choice("zweiter text", "eins"),
                    "zwei": Choice("dritter text", "zwei"),
                },
                "PROPERTY 'test' = 1",
            ),
            "eins": Dialog(
                "eins",
                "zweiter text",
                {
                    "drei": Choice("vierter text", "drei"),
                },
            ),
            "zwei": Dialog(
                "zwei",
                "dritter text",
                {},
            ),
        },
        "My Story",
    )


def test_simple_markdown():
    story = get_simple_test_story()
    assert_only_non_empty_lines(
        story.to_markdown(),
        """# My Story
## Coole ID
LOGIC PROPERTY 'test' = 1

Text
- eins: zweiter text
- zwei: dritter text

## eins
zweiter text
- drei: vierter text

## zwei
dritter text

""",
    )


def test_secrets():
    story = get_simple_test_story()
    story.secretsummary = "This is a secret summary\n### Heading"
    assert_only_non_empty_lines(
        story.to_markdown(),
        """# My Story
SECRET This is a secret summary
SECRET ### Heading
## Coole ID
LOGIC PROPERTY 'test' = 1

Text
- eins: zweiter text
- zwei: dritter text

## eins
zweiter text
- drei: vierter text

## zwei
dritter text

""",
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
    assert len(story.prevdialogids) == 2
    story.back_dialog()
    assert len(story.prevdialogids) == 1
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
    assert_only_non_empty_lines(md, story.to_markdown())


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


def test_markdown_from_history():
    story = get_simple_test_story()
    story.next_dialog("eins")
    assert_only_non_empty_lines(
        story.markdown_from_history(includelogic=True),
        """# My Story

## Coole ID
LOGIC PROPERTY 'test' = 1

Text
- eins: zweiter text
- zwei: dritter text

## eins
zweiter text
- drei: vierter text

LOGIC PROPERTY "test" = 1
""",
    )
    assert_only_non_empty_lines(
        story.markdown_from_history(includelogic=False),
        """# My Story

## Coole ID

Text
- eins: zweiter text
- zwei: dritter text

## eins
zweiter text
- drei: vierter text
""",
    )
    assert_only_non_empty_lines(
        story.markdown_from_history(historylen=1, includelogic=False),
        """# My Story

## eins
zweiter text
- drei: vierter text
""",
    )
