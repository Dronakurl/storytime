# Storytime
## View and create interactive stories
With storytime, you can create fun interactive stories. 
Just write a markdown file with your dialogues. 
An example file can be found in [`data/story.md`](data/story.md).
You can also create a story with the built-in openai integration.

## Installation
Storytime needs `python` and the `textual` package. All python dependencies are shown in the file `pyproject.toml`. 
Install with `poetry`:
```
poetry install
```
If you don't like `poetry`, you can install with `pip`:
```
pip install -r requirements.txt 
```

## Start the textual app
Run Storytime with (or without the `poetry run` part):
```
poetry run textual run app.py
```

## Integration with openai
To use the openai integration, you need to set the environment variable `OPENAI_API_KEY` to your openai api key.
You can get your api key from the [openai settings](https://platform.openai.com/account/api-keys).

```[tasklist]
### Todos
- [ ] system prompt in `gptstory.py` to set the story
- [ ] Check if other languages are working
- [ ] Continue function to build larger stories
- [ ] include statistics of the story in the Header and after the generation of the story
- [ ] More example stories
- [ ] A gif for the README.md
- [ ] Webserver to view the story in a browser, convert the python code in `app.py` with chatgpt
- [ ] Continue the story from a certain point locking the previous history, prompt with locked headlines
- [ ] Network analyzer to find isolated storylines and to enable gpt continuation of larger storylines
- [ ] Images with DALL-E based on the dialogues
- [ ] Separation of packages and subpackages, so that the Story class can more easily be used in other projects
- [ ] Settings screen, with export, import of current story history
- [ ] Settings dataclass: Storyfile, backup directory
- [ ] Write, backup the markdown file of generated story
- [ ] Restrict exec function to only a few commands
```
