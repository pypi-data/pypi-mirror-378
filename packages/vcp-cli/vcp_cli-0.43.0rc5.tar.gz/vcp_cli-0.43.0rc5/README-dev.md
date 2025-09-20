# Development

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/chanzuckerberg/vcp-cli.git
   cd vcp-cli
   ```

2. Install development dependencies:
   ```bash
   make setup
   ```

   This will:
   - Install all dependencies using uv
   - Create a default config file at `~/.vcp/config.yaml`

   Alternatively, you can run individual steps:
   ```bash
   uv sync --all-groups  # Install dependencies
   ```

## Commands

Available development commands:
   ```
  make help      - Show this help message
  make setup     - Initial setup (install deps, create config)
  make install   - Install dependencies using uv
  make build     - Build the package
  make test      - Run tests
  make lint      - Run linting checks
  make lint-fix  - Format code and fix linting issues
  make clean     - Clean up build artifacts
  make dev       - Run in development mode
  make 
   ```

Run the CLI:
* Option 1: `make dev --help`
* Option 2: `uv run vcp --help`

