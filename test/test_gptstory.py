from gptstory import StoryGenerator
from story import Story


def test_storygenerator():
    for current, chunk in StoryGenerator(
        prompt="The story is about a pirate. The story should be complete so no dangling choices.",
        stream=True,
    ).generate_story(temperature=0, max_tokens=400):
        print(chunk)

    print(current)
    s = Story.from_markdown(current)
    assert s.check_integrity()
    assert len(s.dialogs) > 0
