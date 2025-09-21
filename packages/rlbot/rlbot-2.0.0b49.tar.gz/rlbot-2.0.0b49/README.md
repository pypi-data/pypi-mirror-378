# RLBot Python Interface

A high performance Python interface for communicating with RLBot v5.

## Making a bot with this interface

See this video tutorial on YouTube for a quick start guide: <https://www.youtube.com/watch?v=GLqvodQ942A>

Also see the [main RLBot wiki](https://wiki.rlbot.org/) (make sure to avoid info on v4) and also see [this project's wiki](https://github.com/RLBot/python-interface/wiki)

## Dev setup

The following is how to setup a development environment for this project, NOT how to create a bot using this interface!

- Ensure Python 3.11+ is installed
- Create a virtual Python environment
  - `python3 -m venv venv`
- Activate the virtual environment
  - Windows: `venv\Scripts\activate.bat`
  - Linux: `source venv/bin/activate`
- Install the package
  - `pip install --editable .`
  - This will install the package in editable mode,
  meaning you can make changes to the code, and they
  will be reflected in the installed package without
  having to run the command again
- If you are making changes involving the flatbuffer schema and
  [flatbuffers_python](https://github.com/RLBot/flatbuffers-python),
  also install your local copy of that package in editable mode:
  - `pip uninstall rlbot_flatbuffers`
  - `pip install --editable <path/to/rlbot_flatbuffers>`

This project is formatted using [Ruff](https://docs.astral.sh/ruff/formatter/).

- Install: `pip install ruff`.
- Sort imports: `ruff check --select I --fix`
- Format code: `ruff format`

## Testing

- You can test launching a match with `python tests/runner.py`

## Building

- You can build the package with `python -m build`
  - Note: You might have to `pip install -U build` first
  - `rlbot-5.0.0-py3-none-any.whl` and `rlbot-5.0.0.tar.gz`
  will be created in the `dist` folder
