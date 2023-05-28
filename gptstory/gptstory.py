import os
import time

import openai

from story import Story

gptstory = True
apikey = os.getenv("OPENAI_API_KEY")
if apikey is None:
    print("OPENAI_API_KEY not set")
    gptstory = False
openai.api_key = apikey


class StoryGenerator:
    """Generate a story from a prompt."""

    with open("data/minimal.md", "r") as f:
        storytemplate = f.read()

    def __init__(
        self,
        prompt: str = "The story is about a pirate",
        stream: bool = True,
    ):
        """Initialize the story generator.

        :param prompt: The prompt to use to generate the story. It should be a brief description of the story.
        :param stream: Whether to stream the results or not.
        :returns: None
        """
        self.prompt = prompt
        self.stream = stream
        self.generateprompt = (
            "Write a story for a text based role playing program, that has this example syntax. Return as markup code that can be copied into a text editor. \n\n ```\n "
            + self.storytemplate
            + "\n```\n\n "
            + self.prompt
        )
        self.current_result = ""
        self.delta = ""

    def generate_story(self, **kwargs):
        """Generate a story from a prompt.

        :param kwargs: Keyword arguments to pass to chatgpt
        :returns: a generator that yields the state of the current story and the delta that was just added
                when stream is True, otherwise returns the full story
        """
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            # model="text-ada-001",
            messages=[
                {
                    "role": "system",
                    "content": "You are an author writing a story for a text based role playing program. You write the story in the syntax of the following example. You write a story based on the prompt that is given to you in the same language.  Keep the keyword LOGIC in English. \n\n ```\n "
                    + self.storytemplate
                    + "\n ```\n",
                },
                {"role": "user", "content": self.prompt},
            ],
            stream=self.stream,
            **kwargs,
        )
        if not self.stream:
            return completion.choices[0].message.content
        else:
            for chunk in completion:
                self.delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                if self.delta is None:
                    self.delta = ""
                self.current_result += self.delta
                yield self.current_result, self.delta

    def generate_story_from_file(self, fname: str = "data/story.md"):
        """Generate a story from a file.

        :param fname: The name of the file to read from.
        :returns: a generator that yields the state of the current story and the delta that was just added
        """
        self.current_result = ""
        with open(fname, "r") as f:
            for line in f:
                time.sleep(0.1)
                self.delta = line
                self.current_result += self.delta
                yield self.current_result, self.delta

    def write_story(self, fname: str = "story.md"):
        """Write the current story to a file.

        :param fname: The name of the file to write to.
        :returns: A list of errors that were found in the story.
        """
        self.story = Story.from_markdown(self.current_result)
        errors = []
        if not self.story.check_integrity():
            errors = self.story.prune_dangling_choices()
            print("Pruned dangling choices: \n" + "\n".join(errors))
        self.story.markdown_file = fname
        self.story.save_markdown()
        return errors


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python gptstory.py <prompt>")
        exit(1)
    elif len(sys.argv) > 2:
        print("Warning: Only the first argument will be used as the prompt")
        print("Usage: python gptstory.py <prompt>")
        exit(1)
    sg = StoryGenerator(prompt=sys.argv[1])
    for story, delta in sg.generate_story():
        print(delta, end="")
    print("\n\n Writing story to story.md")
    sg.write_story("story.md")
