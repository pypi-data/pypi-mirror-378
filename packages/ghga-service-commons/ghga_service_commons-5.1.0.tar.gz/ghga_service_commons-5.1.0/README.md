![tests](https://github.com/ghga-de/ghga-service-commons/actions/workflows/tests.yaml/badge.svg)
[![PyPI version shields.io](https://img.shields.io/pypi/v/ghga_service_commons.svg)](https://pypi.python.org/pypi/ghga_service_commons/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ghga_service_commons.svg)](https://pypi.python.org/pypi/ghga_service_commons/)
[![Coverage Status](https://coveralls.io/repos/github/ghga-de/ghga-service-commons/badge.svg?branch=main)](https://coveralls.io/github/ghga-de/ghga-service-commons?branch=main)

# ghga-service-commons
This Python library serves as a collection of common utilities used by
the microservices developed at German Human Genome-Phenome Archive (GHGA).

It collects boilerplate code for common functionalities such as API server setup,
authentication and authorization.

This library is primarily intended for internal use at GHGA and should
not be seen as a general-purpose microservice chassis.
However, if this library matches your specific needs as well,
please feel free to use it. It is open source.

# Installation
This package is available at PyPI:
https://pypi.org/project/ghga_service_commons

You can install it from there using:
```
pip install ghga_service_commons
```

Thereby, you may specify following extra(s):
- `api`: dependencies needed to use the API server functionalities
- `auth`: dependencies needed for dealing with authentication and authorization

## Development
For setting up the development environment, we rely on the
[devcontainer feature](https://code.visualstudio.com/docs/remote/containers) of vscode.

To use it, you have to have Docker as well as vscode with its "Remote - Containers"
extension (`ms-vscode-remote.remote-containers`) extension installed.
Then, you just have to open this repo in vscode and run the command
`Remote-Containers: Reopen in Container` from the vscode "Command Palette".

This will give you a full-fledged, pre-configured development environment including:
- infrastructural dependencies of the service (databases, etc.)
- all relevant vscode extensions pre-installed
- pre-configured linting and auto-formatting
- a pre-configured debugger
- automatic license-header insertion

Moreover, inside the devcontainer, there is following convenience command available
(please type it in the integrated terminal of vscode):
- `dev_install` - install the lib with all development dependencies and pre-commit hooks
(please run that if you are starting the devcontainer for the first time
or if added any python dependencies to the [`./pyproject.toml`](./pyproject.toml))

If you prefer not to use vscode, you could get a similar setup (without the editor specific features)
by running the following commands:
``` bash
# Execute in the repo's root dir:
cd ./.devcontainer

# build and run the environment with docker-compose
docker build -t ghga-service-commons .
docker run -it ghga-service-commons /bin/bash

```

## License
This repository is free to use and modify according to the [Apache 2.0 License](./LICENSE).
