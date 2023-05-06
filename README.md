# Storytime
## A terminal (TUI) app to view interactive stories.
With storytime, you can create fun interactive stories. 
Just write a markdown file with your dialogues. 
An example file can be found in `data/story.md`.

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

## Usage
Run Storytime with (or without the `poetry run` part):
```
poetry run textual run app.py
```


## TODO
- State of the story in the story class
- Settings screen, with export, import of current story history
- Settings dataclass: Storyfile, backup directory
- Add choice option
- Write the markdown file 
- Backup the markdown file
- Error correction in the story parser
- Copilot or other integration for story completion
- Some kind of healthpoint system
- fights with monsters or something

