# forklift
[![Python application](https://github.com/IUBLibTech/forklift/actions/workflows/python-app.yml/badge.svg)](https://github.com/IUBLibTech/forklift/actions/workflows/python-app.yml)

Listener for Docker Hub webhooks.

## Installation
`pip install -r requirements.txt`

`python forklift.py`

## Configuration
- Copy `example.config` to `forklift.config`
- Set a secure `api_key`
- Set `docker_root` to the directory that the target script is run relative to.
- Setup `valid_containers`
  - Top level key is `{repository name}/{image_name}`.
  - `tag` allows only the specified tag to trigger the `target` script. This is interpreted as a regular expression.
  - `target` is a path relative to `docker_root` to the script to run.
- Create a Docker Hub webhook that calls `https://your_host/hook?apikey={your_apikey}`

## Development
`pip install -r requirements_dev.txt`

### Design Notes
The shell command used to restart a container should use only strings from the program configuration,
and must not contain any fragments sourced from the request data.

### Running Tests
`pytest`
