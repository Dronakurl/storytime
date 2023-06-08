# Storytime!

## View and create interactive stories in terminal

With `storytime`, you can create fun interactive stories in your terminal.
Just write a markdown file with your dialogues, choices and simple logic.
An example file can be found in [`storytime_ai/templates/minimal.md`](storytime_ai/templates/minimal.md).
You can also create a story with the built-in [openai](https://openai.com) integration.

- A _web version_ is planned
- _storytime_ai_ is the name of the python package

![screenshot](assets/readme.webp "Screenshot of Storytime")

## Installation

- Install the latest version with `pip`:

  ```
  pip install 'git+https://github.com/Dronakurl/storytime.git#egg=storytime_ai[extras]'
  ```

- Set environment variable with openai api key (optional)

  To use the story generation with openai, you need to set the environment variable
  `OPENAI_API_KEY` to your openai api key.
  You can get your api key from the [openai settings](https://platform.openai.com/account/api-keys).
  The environment variable can be set in a file `.env` in the root directory of this project.

  ```[.env]
  OPENAI_API_KEY="sk-p9GOXXXXX<Your OPENAI_API_KEY>"
  ```

## Start the Storytime terminal app

Run Storytime with:

```
storytime [markdown_file with your own story]
```

### Helper script: Check integrity of your story

You can check if your story is valid with the following command:

```
storytime-checker [markdown_file with your own story]
```

It will check if all the choices are valid and if all dialogues are connected.

## Development

See [test/README.md](test/README.md) for more information about the packaging.
See the issues for planned features.

### Install storytime from github

- Clone the repository:

  ```
  git clone https://www.github.com/Dronakurl/storytime
  ```

- Install [`poetry`](https://python-poetry.org/) if you don't have it yet

  ```
  curl -sSL https://install.python-poetry.org | python3 -
  ```

- Install using poetry:

  ```
  poetry install --all-extras
  ```

- Run tests:
  ```
  poetry run pytest
  ```
