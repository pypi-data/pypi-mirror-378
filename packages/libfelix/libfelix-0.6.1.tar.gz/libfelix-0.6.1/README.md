# libfelix
Felix' library of snippets.

- few dependencies
- keep it simple


## Installation
```
pip install libfelix
```


## libfelix.git
```python
>>> from libfelix.git import Repo
>>> r = Repo('.')
>>> r.head
'9e260ece8558ba9a6c4ad6a9c89905630fe0140b'
```


## libfelix.music
TBA


## libfelix.logging
Structlog shortcut for fast development with opinionated settings, i.e.

- log to STDERR
- configure the log level by setting the environment variable `LOGLEVEL`

```python
from libfelix.logging import configure_structlog_console, get_logger

configure_structlog_console()
log = get_logger()
log.info('...')
```


## Development
```
mise trust
mise install
pre-commit install -f
uv sync --all-extras
```
