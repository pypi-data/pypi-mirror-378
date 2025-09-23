# LV Name API

LV Name API is a Python module for generating Latvian-style names.
It supports both programmatic use and a simple CLI for quick access.

## Features

* Generate random Latvian first names and last names.
* Easy-to-use Python API.
* Command-line interface for quick name generation.
* Configurable options stored in `config.json` (optional).
* First-run detection with guidance for new users.

## Installation

Install via pip:

```bash
pip install lv-name-api
```

## Usage

### Python API

```python
from latvian_names import core

# Generate a random name
name = core.get_random_name()
print(name)

# Access settings
from latvian_names import settings
print(settings.get("example_setting"))
```

### CLI

Generate names from the command line:

```bash
latnames
```

Optional flags:

```text
--settings, -set, -setup, --setup    # Access configuration menu
--debug                              # Enable debug mode
--noreboot                            # Disable automatic reboot
```

### First Run

On the first run, LV Name API will display:

```
First run detected!
- Your configuration file can be optionally saved as config.json
- Run `--settings` to customize settings
```

## Notes

This project is made by an independent developer in his free time for fun. You can freely use and integrate it in your projects.

## License

This project is licensed under the **MIT License**.
