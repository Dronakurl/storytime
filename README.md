# Storytime!

## View and create interactive stories in terminal

### (web version planned)

With storytime, you can create fun interactive stories in your terminal.
Just write a markdown file with your dialogues, choices and simple logic.
An example file can be found in [`data/minimal.md`](data/minimal.md).
You can also create a story with the built-in [openai](https://openai.com) integration.

## Installation

Storytime needs `python`. Install with [`poetry`](https://python-poetry.org/).

```
poetry install --all-extras
```

If you don't like `poetry`, you can install with `pip`:

```
pip install -r requirements.txt
```

Poetry automatically sets the environment variable from a `.env` file using the poetry package `python-dotenv` which is installed with poetry.:

```
poetry add python-dotenv
```

## Start the Storytime terminal app

Run Storytime with (or without the `poetry run` part, if you installed with `pip`):

```
poetry run textual run app.py
```

## Integration with openai

To use the openai integration, you need to set the environment variable `OPENAI_API_KEY` to your openai api key.
You can get your api key from the [openai settings](https://platform.openai.com/account/api-keys).
The environment variable can be set in a file `.env` in the root directory of this project.
