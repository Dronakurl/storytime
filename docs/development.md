# Storytime development

This file provides some information for development of storytime.

## Installation of storytime_ai package from local repository

```
deactivate; mkdir /tmp/test; cd /tmp/test; rm -rf venv
python3.11 -m venv venv; source venv/bin/activate

pip install ~/storytime[extras]
cp ~/storytime/.env .
storytime

python3.11 -c "from storytime_ai import Story; Story.from_markdown_file('/home/konrad/storytime/storytime_ai/templates/minimal.md').check_integrity()"
python3.11 -c "from importlib.metadata import version; print(version('storytime_ai'))"
deactivate; rm -rf venv;

```

## Installation of storytime_ai package from github repository

The @0.3.0 installs a specfic tag.

```
deactivate; rm -fr /tmp/test/venv; mkdir /tmp/test; cd /tmp/test; rm -rf venv
python3.11 -m venv venv; source venv/bin/activate

pip install 'git+https://github.com/Dronakurl/storytime.git@0.3.0#egg=storytime_ai[extras]'

python3.11 -c "from storytime_ai import Story; Story.from_markdown_file('/home/konrad/storytime/storytime_ai/templates/minimal.md').check_integrity()"
python3.11 -c "from importlib.metadata import version; print(version('storytime_ai'))"
deactivate; rm -rf venv;
```

## Build storytime PyPI package

In future versions, this package will be available on [PyPI](https://pypi.org/). Here is how to build it, currently only on test.pypi.org, so no one is annoyed by this early version:

I don't know why, but the following command doesn't work for me.

```
poetry config http-basic.pypi <USER> <PASSWORD>
```

Hence, I did it manually. Maybe it works for you. If it works, you can skip the following step.
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
deactivate; mkdir /tmp/test; cd /tmp/test; rm -rf venv
python -m venv venv; source venv/bin/activate

pip install --index-url https://test.pypi.org/simple/ --no-deps storytime_ai[extras]

python -c "from storytime_ai import Story; Story.from_markdown_file('/home/konrad/storytime/storytime_ai/templates/minimal.md').check_integrity()"
python -c "from importlib.metadata import version; print(version('storytime_ai'))"
deactivate; rm -rf venv;
```
