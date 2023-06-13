#!/bin/bash

# A script that runs the sphinx-build and checks the output for errors.
# This script is called by the pre-commit hook.
poetry run sphinx-build -W docs docs/_build 
# > docs/_build/sphinx-build.log 2>&1
if [ $? -ne 0 ]; then
    echo "Sphinx build failed."
    exit 1
fi
