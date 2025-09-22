# rst_previewer/main.py

import typer
import os
from rst_previewer.app import create_gradio_app
from termcolor import cprint, colored

app = typer.Typer()

def find_rst_files(directory: str):
    """Finds all .rst files in the given directory."""
    rst_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".rst"):
                rst_files.append(os.path.join(root, file))
    return rst_files

@app.command()
def main(
    directory: str = typer.Argument(
        ".",
        help="The directory containing the .rst files to view.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
):
    """
    A modern CLI and web-based viewer for reStructuredText files.
    """
    cprint(f"Searching for .rst files in: {colored(directory, 'cyan')}", "green", attrs=["bold"])
    
    rst_files = find_rst_files(directory)

    if not rst_files:
        cprint("No .rst files found in the specified directory.", "red", attrs=["bold"])
        raise typer.Exit()

    cprint("Found the following .rst files:", attrs=["bold"])
    for i, file_path in enumerate(rst_files):
        print(f"  {colored(i + 1, 'cyan')}: {os.path.relpath(file_path, directory)}")

    # Use typer.prompt for user input. The colored prompt string should work in most terminals.
    choice_str = typer.prompt(
        colored("Please choose the main .rst file to render", "yellow", attrs=["bold"]),
        default="1",
        show_default=True,
    )
    
    try:
        selected_index = int(choice_str) - 1
        if not 0 <= selected_index < len(rst_files):
            raise ValueError
    except ValueError:
        cprint("Invalid selection.", "red", attrs=["bold"])
        raise typer.Exit()

    selected_file = rst_files[selected_index]
    
    cprint(f"\nYou selected: {colored(os.path.basename(selected_file), 'cyan')}", "green", attrs=["bold"])
    cprint("Starting the Gradio web viewer...", attrs=["bold"])

    gradio_app = create_gradio_app(selected_file, directory)
    
    # Launch the Gradio app directly in the current process.
    try:
        cprint("Gradio app is starting at http://127.0.0.1:9000", "yellow")
        cprint("Press Ctrl+C to stop the server.", attrs=["dark"])
        
        gradio_app.launch(server_name='0.0.0.0', server_port=9000, show_api=False)

    except KeyboardInterrupt:
        cprint("\nShutting down the server...", "yellow", attrs=["bold"])
        # Gradio handles its own cleanup, so we can just exit gracefully.
        cprint("Server stopped.", "green", attrs=["bold"])
    except Exception as e:
        cprint(f"An error occurred while running the Gradio app: {e}", "red", attrs=["bold"])


if __name__ == "__main__":
    app()

