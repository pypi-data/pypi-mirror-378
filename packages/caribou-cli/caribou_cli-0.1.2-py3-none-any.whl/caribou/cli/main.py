# cli/caribou/src/caribou/__main__.py

import typer

# Import the app for the 'create-system' command
from .create_agent_cli import app as create_system_app

# Import the app for the new 'datasets' command
from .datasets_cli import datasets_app
from .run_cli import run_app
from .config_cli import config_app 
from .utils_cli import utils_app  # <-- Import the utils app
# Main caribou application
app = typer.Typer(
    name="caribou",
    help="CARIBOU: The Open-source Language Agent Framework",
    no_args_is_help=True
)

# Register the command groups
app.add_typer(create_system_app, name="create-system")
app.add_typer(datasets_app, name="datasets")
app.add_typer(run_app, name="run")
app.add_typer(config_app, name="config")  # <-- Register the new config app
app.add_typer(utils_app, name="utils")  # <-- Register the utils app


def main():
    app()

if __name__ == "__main__":
    main()