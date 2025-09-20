# Virtual Cells Platform Command Line Interface

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/chanzuckerberg/vcp-cli/actions)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

A command-line interface for interacting with the Virtual Cell Platform ("VCP").

## Requirements

- 🐍 **[Python 3.10+](https://www.python.org/downloads/)**: Ensure you have Python 3.10 or later installed.


## Installation

```bash
pip install vcp-cli
```

## Usage

### Login

To log in to the VCP platform, use the following command:

```bash
vcp login --username your.email@example.com
```

This command will prompt you to enter your password securely.

### Model Commands

The following commands are available for model management:

- **List Models**: `vcp model list`
- **Download Model**: `vcp model download`
- **Submit Model**: `vcp model submit <yaml_file>` - Submit model data to the VCP Model Hub API

### Data Commands

The following commands are available for data:

- #### Search for Data:
   Allows you to search MDR for authorized datasets by TERM.
   **Command:** `vcp data search <TERM>`
   **Example:** `vcp data search "cryoet"`

- #### Get information about a Dataset:
   Get a summary table with information about id, domain, label, doi, cell_count, species, tissues, and asset location
   **Command:** `vcp data describe <DATASET_ID>`

- #### Download a Dataset:
   Download a specific dataset by id.
   **Command:** `vcp data download [OPTIONS] DATASET_ID`

### Other Commands

Additional commands will be documented here as they are implemented.

## Development

1. Install development dependencies:
   ```bash
   make setup
   ```

2. Run tests:
   ```bash
   make test
   ```

3. Other development commands:
   ```bash
   make lint      # Run linting checks
   make format    # Format code
   make build     # Build the package
   make dev       # Run in development mode
   ```

## Documentation

1. Install docs dependencies:
   ```bash
   uv sync --group docs
   ```

2. Build the documentation:
   ```bash
   cd docs
   uv run make html
   ```

The built artifacts will be in `docs/_build/html`.

## License

[Add your license information here]
