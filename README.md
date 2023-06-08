# Storytime! _storytime_ai_

## View and create interactive stories in terminal _(web version planned)_

With storytime, you can create fun interactive stories in your terminal.
Just write a markdown file with your dialogues, choices and simple logic.
An example file can be found in [`storytime_ai/templates/minimal.md`](storytime_ai/templates/minimal.md).
You can also create a story with the built-in [openai](https://openai.com) integration.

![screenshot](assets/readme.webp "Screenshot of Storytime")

## Installation from github repository

Clone the repository:

```
git clone https://www.github.com/Dronakurl/storytime
```

Install with [`poetry`](https://python-poetry.org/).

```
curl -sSL https://install.python-poetry.org | python3 -
poetry install --all-extras
```

Poetry automatically sets the environment variable from a `.env` file using the poetry package `python-dotenv` which is installed with poetry.:

```
poetry self add poetry-dotenv-plugin
```

## Start the Storytime terminal app

Run Storytime with:

```
poetry run textual run app.py
```

## Integration with openai

To use the openai integration, you need to set the environment variable `OPENAI_API_KEY` to your openai api key.
You can get your api key from the [openai settings](https://platform.openai.com/account/api-keys).
The environment variable can be set in a file `.env` in the root directory of this project.
```[.env]
OPENAI_API_KEY="sk-p9GOXXXXX<Your OPENAI_API_KEY>"
```

## Check integrity of your own story

You can check if your story is valid with the following command:
`poetry run python -c "from storytime_ai import Story; Story.from_markdown_file('yourstory.md').check_integrity()"`
It will check if all the choices are valid and if all dialogues are connected.

## Build storytime package (for developers)

In future versions, this package will be available on pypi. Here is how to build it, currently only on test.pypi.org, so no one is annoyed by this early version:

I don't know why, but

```
poetry config http-basic.pypi <USER> <PASSWORD>
```

doesn't work for me, so you maybe have to do it manually.
Set the file `~/.config/pypoetry/auth.toml` to the following content:

```
[http-basic.pypi]
username = "<USER>"
password = "<PASSWORD>"
```

Then build and publish the package with:

```
poetry build
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish --repository testpypi
```

Test the package with:

```
deactivate
mkdir /tmp/test
cd /tmp/test
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install --index-url https://test.pypi.org/simple/ --no-deps storytime_ai
python -c "from storytime_ai import Story; Story.from_markdown_file('/home/konrad/storytime/storytime_ai/templates/minimal.md').check_integrity()"
python -c "from importlib.metadata import version; print(version('storytime_ai'))"
deactivate
rm -rf venv
cd ~/storytime
```

## Install from github repository (developers only)
```
deactivate
mkdir /tmp/test
cd /tmp/test
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install ~/storytime[extras]
python -c "from storytime_ai import Story; Story.from_markdown_file('/home/konrad/storytime/storytime_ai/templates/minimal.md').check_integrity()"
python -c "from importlib.metadata import version; print(version('storytime_ai'))"
deactivate
rm -rf venv
cd ~/storytime
```
