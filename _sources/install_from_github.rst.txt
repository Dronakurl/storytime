Install storytime from github
-----------------------------

- Clone the repository::

    git clone https://www.github.com/Dronakurl/storytime

- Install `poetry <https://python-poetry.org/>`_ if you don't have it yet::

    curl -sSL https://install.python-poetry.org | python3 -

- Install using poetry::

    poetry install --all-extras

- Run tests::

    poetry run pytest
