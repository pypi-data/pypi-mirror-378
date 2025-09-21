# Brujula

A simple hello world Python package.

## Installation

```bash
pip install brujula
```

## Usage

```python
from brujula import hello_world

# Use the hello_world function
message = hello_world()
print(message)  # Output: Hello, world!
```

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Setup

```bash
uv sync
```

### Run

```bash
uv run python main.py
```

## License

MIT License
