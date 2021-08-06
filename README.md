# forklift
[![Python application](https://github.com/IUBLibTech/forklift/actions/workflows/python-app.yml/badge.svg)](https://github.com/IUBLibTech/forklift/actions/workflows/python-app.yml)

Listener for Docker Hub webhooks.

## Installation
`pip install -r requirements.txt`

`python forklift.py`

## Configuration
- Copy `forklift.config.example` to `forklift.config`
- Set a secure `api_key`
- Set `docker_root` to the directory that the target script is run relative to.
- Setup `valid_containers`
  - Top level key is `{repository name}/{image_name}`.
  - `target` points to a script to run inside `docker_root`.
  - `tag` allows only the specified tag to trigger the `target` script.

## Development
`pip install -r requirements_dev.txt`

### Running Tests
`pytest`
