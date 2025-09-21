"""Module for CTF management commands."""
from pathlib import Path
import os

from ctf_orchestrator.utils.state import StateManager
from ctf_orchestrator.utils.themes import print_success, print_error
from dotenv import load_dotenv

import typer
from rich import print as print_rich
from rich.progress import Progress, SpinnerColumn, TextColumn



app = typer.Typer()



load_dotenv()
ENV = os.getenv("ENVIRONMENT", "PROD")

state_manager = StateManager()

@app.command()
def init(ctf_name, directory=Path.cwd(), auto_active=True):
    """
    Initialize a CTF directory.
    """
    try:
        # check if ctf_name is already recorded in state file
        state_dict = state_manager.get_state()
        if ctf_name in state_dict["ctfs"]:
            raise ValueError(f"The CTF {ctf_name} has already been initialized.")
        ctf_directory_path = Path(directory) / ctf_name
        if (ctf_directory_path).exists():
            raise ValueError(f"The CTF directory {ctf_directory_path} already exists")
        with Progress(SpinnerColumn(),TextColumn("[progress.description]{task.description}"),
        transient=True,) as progress:
            progress.add_task(description="Preparing directory...", total=None)
            ctf_directory_path.mkdir(parents=True)
        print_success(f"CTF directory successfully created at {ctf_directory_path}.")
        state_manager.add_ctf(ctf_directory_path, ctf_name)
        print_success(f"Added {ctf_name} to CTF list.")

        if auto_active:
            state_manager.set_active_ctf(ctf_name)
            print_success(f"Set {ctf_name} as the active CTF.")


    except Exception as e:
        print_error(f"[b red]Error: [/b red]{e}")

        if ENV == "DEV":
            raise e
        raise typer.Exit(code=1)

@app.command()
def activate(ctf_name):
    """
    Activate a CTF as the current active CTF.
    """
    try:
        state_dict = state_manager.get_state()
        previous_active_ctf = state_dict["active_ctf"]
        state_manager.set_active_ctf(ctf_name)
        print_success(f"Set {ctf_name} as active CTF{ f" and deactivated {previous_active_ctf}" if previous_active_ctf and previous_active_ctf!=ctf_name else ""}.")
    except Exception as e:
        print_error(f"[b red]Error: [/b red]{e}")
        if ENV == "DEV":
            raise e
        raise typer.Exit(code=1)

@app.command()
def deactivate():
    """
    Deactivate the current active CTF.
    """
    try:
        state_dict = state_manager.get_state()
        if state_dict["active_ctf"] == "":
            raise ValueError("There is no currently active CTF.")
        previous_active_ctf = state_dict["active_ctf"]
        state_manager.set_active_ctf("")
        print_success(f"Deactivated {previous_active_ctf}.")
    except Exception as e:
        print_error(f"[b red]Error: [/b red]{e}")
        if ENV == "DEV":
            raise e
