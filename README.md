## Gitea Test Scenario
This repository contains test scenario for Gitea service. The scenario relies that the tests are executed sequentially.

## Setting up

1. Install python 3.10 (instructions below for Mac OS). 
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
1. Install the requirements: `pip install -r requirements.txt`.
1. Install Docker from the [Docker official page](https://www.docker.com/).


## Launching the tests

1. Ensure docker desktop is running.
1. `cd <repo_root>`
1. `pytest .`
