# Styling
.PHONY: style
style:
    black .
    flake8
    isort .


# # Environment
# .ONESHELL:
# venv:
#     python3 -m venv venv
#     source venv/bin/activate
#     python3 -m pip install pip setuptools wheel
#     python3 -m pip install -e .

.PHONY: help
help:
    @echo "Commands:"
    @echo "venv    : creates a virtual environment."
    @echo "style   : executes style formatting."
    @echo "clean   : cleans all unnecessary files."
