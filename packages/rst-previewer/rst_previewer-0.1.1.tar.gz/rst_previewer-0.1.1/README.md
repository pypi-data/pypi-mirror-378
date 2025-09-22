# rst-previewer

A modern CLI tool that finds reStructuredText (.rst) files in a directory and displays them in a clean, web-based Gradio interface. Perfect for quickly previewing documentation, articles, or notes without a full Sphinx build.

<img src="https://raw.githubusercontent.com/rohanmohapatra/rst-previewer/main/docs/images/hero.png">

## Installation
This tool is designed to be installed and run in an isolated environment using pipx. This avoids cluttering your global Python installation.

#### Install rst-previewer:
```sh
pipx install rst-previewer
```

That's it! The `rst-previewer` command is now available anywhere in your terminal.

## Usage

#### Select a file from a directory:
```
rst-previewer /path/to/your/project/docs/
```
The tool will print a local URL to your terminal. Open this URL in your web browser to see the rendered document.

## Development Guide

Interested in contributing? Setting up a development environment is easy.

#### Prerequisites
- Git
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) 

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.