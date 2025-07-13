# JupyterLab Firefox Launcher

A JupyterLab extension to launch Firefox in a tab.

## Description

This extension adds a Firefox launcher to JupyterLab, allowing you to open Firefox directly within the JupyterLab interface.

## Installation

```bash
pip install jupyterlab-firefox-launcher
```

## Development

### Prerequisites

- Python 3.8+
- Node.js
- Yarn

### Setup

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -e .
   ```
3. Install and build the frontend:
   ```bash
   yarn install
   yarn build
   ```

### Building

To build the extension:

```bash
yarn build
python -m build
```

## License

BSD-3-Clause License
