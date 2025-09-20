# Trainwave Jupyter Extension

Make trainwave.ai available right in your notebook for fast, cheap and efficient GPU workloads.

This extension is composed of a Python package named `trainwave-jupyter`
for the server extension and a NPM package named `trainwave-jupyter`
for the frontend extension.

## Development

This project uses `uv` for Python dependency management and includes a comprehensive Makefile for development tasks.

### Setup

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# We need jupyterlab ahead of time to build frontend
pip install jupyterlab
```

1. `make dev` -- this will build and run the watch command to refresh automatically on changes.
2. In another shell run `make run-server` which will start the actual notebook server
