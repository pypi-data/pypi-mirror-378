"""Module for challenge management commands in the active CTF."""
import json
from pathlib import Path

import os
from dotenv import load_dotenv

import typer

from ctf_orchestrator.utils.state import StateManager
from ctf_orchestrator.utils.themes import print_success, print_error


from rich import print as print_rich
from rich.progress import Progress, SpinnerColumn, TextColumn


app = typer.Typer()
load_dotenv()
ENV = os.getenv("ENVIRONMENT", "PROD")

state_manager = StateManager()

@app.command()
def add(chal_name, category, points = 0, solved = False, auto_active = True):
    """
    Add a CTF Challenge to the Active CTF.
    """
    try:
        # check active
        ctf_obj = state_manager.get_ctf()
        state_dict = state_manager.get_state()

        # check if challenges already exists
        if chal_name in ctf_obj["challenges"].keys():
            raise ValueError(f"Challenge {chal_name} already exists in {state_dict["active_ctf"]}.")
        
        state_manager.add_chal(chal_name, category, points, solved)
        print_success(
            f"Added {chal_name} to {state_dict["active_ctf"]} in the {category} category."
            )
        if auto_active:
            state_manager.set_active_chall(chal_name)
            print_success(f"Set {chal_name} as active challenge.")

        challenge_path = Path(ctf_obj["directory"])

        with Progress(SpinnerColumn(),TextColumn("[progress.description]{task.description}"),
        transient=True,) as progress:
            progress.add_task(description="Preparing directory...", total=None)
            (challenge_path / category / chal_name).mkdir(parents = True)
        print_success(f"Created directories for {chal_name}.")

    except Exception as e:
        print_error(f"[b red]Error: [/b red]{e}")

        if ENV == "DEV":
            raise e
        raise typer.Exit(code=1)

@app.command()
def activate(chal_name):
    """
    Activate a CTF challenge in the active CTF
    """
    try:
        ctf_obj = state_manager.get_ctf()
        previous_active_challenge = ctf_obj["active_challenge"]

        state_manager.set_active_chall(chal_name)
        print_success(f"Set {chal_name} as active challenge{ f" and deactivated {previous_active_challenge}" if previous_active_challenge and previous_active_challenge!=chal_name else ""}.")
    except Exception as e:
        print_error(f"[b red]Error: [/b red]{e}")
        if ENV == "DEV":
            raise e
        raise typer.Exit(code=1)
    

@app.command()
def deactivate():
    """
    Deactivate the current active challenge in the active CTF
    """
    try:
        ctf_obj = state_manager.get_ctf()
        state_dict = state_manager.get_state()
        if ctf_obj["active_challenge"] == "":
            raise LookupError(f"There is currently no active challenge in {state_dict["active_ctf"]}")
        previous_active_challenge = ctf_obj["active_challenge"]
        state_manager.set_active_chall("")
        print_success(f"Deactivated {previous_active_challenge}.")
    except Exception as e:
        print_error(f"[b red]Error: [/b red]{e}")
        if ENV == "DEV":
            raise e
        raise typer.Exit(code=1)
    

@app.command()
def solve(chal_name="", flag=""):
    """
    Mark a challenge (the active challenge by default) in the active CTF as solved.
    """
    try:
        state_dict = state_manager.get_state()
        state_file_path = state_manager.get_state_file_path()
        ctf_obj = state_manager.get_ctf()

        selected_name = ctf_obj["active_challenge"] if chal_name == "" else chal_name

        chall_obj = state_manager.get_chal(chal_name=selected_name)
        if chall_obj["solved"] is True:
            raise ValueError(f"{selected_name} has already been solved.")
        state_dict["ctfs"][state_dict["active_ctf"]]["challenges"][selected_name]["solved"] = True

        if flag != "":
            state_dict["ctfs"][state_dict["active_ctf"]]["challenges"][selected_name]["flag"] = flag
        with open(state_file_path, "w", encoding="utf-8") as f:
            json.dump(state_dict, f)
        print_rich(f"Great job on solving {selected_name}! You've been awarded {chall_obj["points"]} points.\n{"" if chal_name != "" else "Activate your next challenge using [b]flag activate[/b]."}")
        state_manager.set_active_chall("")
    except Exception as e:
        print_error(f"[b red]Error: [/b red]{e}")

        if ENV == "DEV":
            raise e
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()