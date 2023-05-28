# Storytime
## View and create interactive stories in your terminal (web version planned)
With storytime, you can create fun interactive stories in your terminal. 
Just write a markdown file with your dialogues, choices and simple logic. 
An example file can be found in [`data/story.md`](data/story.md).
You can also create a story with the built-in [openai](https://openai.com) integration.

## Installation
Storytime needs `python`. Install with [`poetry`](https://python-poetry.org/).
```
poetry install
```

If you don't like `poetry`, you can install with `pip`:
```
pip install -r requirements.txt 
```

## Start the storytime terminal app
Run Storytime with (or without the `poetry run` part, if you installed with `pip`):
```
poetry run textual run app.py
```

## Integration with openai
To use the openai integration, you need to set the environment variable `OPENAI_API_KEY` to your openai api key.
You can get your api key from the [openai settings](https://platform.openai.com/account/api-keys).
The `OPENAI_API_KEY` can be set in the `.env` file in the root directory of this project.
You will also nedd the poetry package `python-dotenv`:
``` 
poetry add python-dotenv
```

