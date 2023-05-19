## Gitea Test Scenario
This repository contains test scenario for Gitea service. The scenario relies that the tests are executed sequentially.

## Setting up

**NOTE**: The instruction below is shown for MacOS.
1. Install Homebrew [Official page - Homebrew](https://brew.sh/).
   1. `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.
1. Install `pyenv`. [PyEnv - Documentation on GitHub](https://github.com/pyenv/pyenv).
   1. `brew install pyenv`.
   1. Add to your profile (e.g. `~/.zshrc`) `eval "$(pyenv init -)"` to turn on `pyenv`.
1. Install `Python 3.10.0`.
   1. `pyenv install 3.10.0`.
1. Install `pyenv-virtualenv`.
   1. `brew install pyenv-virtualenv`.
1. Create a new virtual environment.
   1. `pyenv virtualenv 3.10.0 gitea`.
1. Restart your Shell.
1. To make this interpreter default for the project
   1. `cd <repo root>`
   1. run `pyenv local gitea`
1. Install the requirements: `pip install -r requirements.txt`.
1. Install Docker from the [Docker official page](https://www.docker.com/).


## Configure the IDE

1. Install PyCharm from [Official page](https://www.jetbrains.com/pycharm/).
1. Open the repo root as a new project.
1. Mark test directory: `test_gitea` - tests root. Right click to do so.
1. Set `pyenv gitea` as the project interpreter.


## Launching the tests

1. Ensure docker desktop is running.
1. `cd <repo_root>`
1. `pytest test_gitea/`
