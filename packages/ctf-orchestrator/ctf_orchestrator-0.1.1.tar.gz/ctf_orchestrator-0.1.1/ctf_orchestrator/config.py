"""Module for configuration related commands."""
from pathlib import Path

import os
from dotenv import load_dotenv

import typer

from ctf_orchestrator.utils.state import StateManager
from ctf_orchestrator.utils.themes import print_info


app = typer.Typer()

load_dotenv()
ENV = os.getenv("ENVIRONMENT", "PROD")

state_manager = StateManager()

@app.command()
def setup():
    """
    Setup the configuration in the /.ctf-orch.'
    """
    # Set up the state
    try:
        if not state_manager.check_state(err=False):
            state_manager.get_state()

        print_info("Setup complete")
    except Exception as e:
        print(f"[b red]Error: [/b red]{e}")
        if ENV == "DEV":
            raise e
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()