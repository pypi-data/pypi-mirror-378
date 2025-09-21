"""Entry point for the CLI application"""
from pathlib import Path
from enum import Enum

import subprocess
import os
from typing import List

from dotenv import load_dotenv
import typer
from typing_extensions import Annotated
from rich import print as print_rich
from rich.panel import Panel
from rich.table import Table

from art import text2art

from ctf_orchestrator.challenge import app as challenge_app
from ctf_orchestrator.config import app as config_app
from ctf_orchestrator.ctf import app as ctf_app

from ctf_orchestrator.utils.themes import print_info, print_warning, print_success, print_error
from ctf_orchestrator.utils.state import StateManager


load_dotenv()
ENV = os.getenv("ENVIRONMENT", "PROD")

state_manager = StateManager()

app = typer.Typer()
app.add_typer(challenge_app, name="challenge", help="Manage challenges tracked in the active CTF.")
app.add_typer(config_app, name="config", help="Change configurations used.")
app.add_typer(ctf_app, name="ctf", help="Manage CTFs tracked.")

@app.command()
def info():
    """
    Display information about the current stateuration and active CTF.
    """
    print_rich(f"[blue]{text2art("CTF ORCH")}[/blue]")
    print_rich("[b]Capture the chaos with a orchestrated workflow.[/b]\n")
    state_exists = state_manager.check_state(err=False)
    if not state_exists:
        print_info("To begin, please run [tt]ctforch config setup[/tt]")
    else:
        state_dict = state_manager.get_state()
        info_table = Table(box=None,
                           show_header=False,
                           padding=(0, 1))
        info_table.add_column(justify="left",
                              style="bold")
        info_table.add_column(justify="left")
        has_active_ctf = state_manager.check_ctf(err=False) 
        info_table.add_row(
            "Active CTF:", f"[blue]{state_dict['active_ctf']}[/blue]" if has_active_ctf else "None"
            )
        if has_active_ctf is False:
            info_table.add_row("Active Challenge: ", "None")
        else:
            active_ctf_dict = state_manager.get_ctf()
            info_table.add_row("Active Challenge: ", f"[blue]{active_ctf_dict['active_challenge']}[/blue]" if active_ctf_dict['active_challenge'] != "" else "None")
        print_rich(Panel(info_table, padding=(1, 2), 
                        title="[b blue]Status[/b blue]",
                        title_align="left",
                        border_style="blue",))

class CleanupOptions(str, Enum):
    """
    Options for cleanup command.
    """
    CTF = "ctf"
    CHALLENGE = "chal"

@app.command()
def cleanup(mode: Annotated[CleanupOptions, typer.Option(prompt=True)]):
    """
    Delete non-existing CTFs or challenges from the active CTF.
    """
    state_dict = state_manager.get_state()
    if mode.value == "ctf":
        print_rich(f"{len(state_dict["ctfs"])} [blue not bold]CTF(s) found.[/blue not bold]")
        removed_counter, not_exists_counter = 0, 0
        initial_active_ctf = state_dict["active_ctf"]
        if len(state_dict["ctfs"]) >0:
            with typer.progressbar(state_dict["ctfs"].copy(), label="Cleaning up your CTFs") as progress:
                for name in progress:
                    ctf_dict = state_dict["ctfs"][name]
                    ctf_directory = Path(ctf_dict["directory"])
                    if not ctf_directory.exists():
                        not_exists_counter += 1
                        print_warning(f"\n\n[orange1]CTF not found: [/orange1]{name} at {ctf_directory}.")
                        delete_input = typer.confirm(f"Do you want to remove {name} from the CTF list?")
                        if not delete_input:
                            print("Skipping...")
                        else:
                            removed_counter += 1
                            state_manager.remove_ctf(name)
                            print_success(f"{"Deactivated and r" if initial_active_ctf == name else "R"}emoved {name}[green] from the CTF list.")
            
        if removed_counter == 0 and not_exists_counter == 0:
            print_success("All CTFs are valid and existing.", True)
        else:
            print_success(f"Cleanup complete.", True)
            print_info(f"Found {not_exists_counter}[green] non-existing CTF{'s' if not_exists_counter > 1 else ''} and removed {removed_counter} CTF{'s' if removed_counter > 1 or removed_counter == 0 else ''}.", True)
            if not_exists_counter-removed_counter > 0:
                print_warning("It is recommended you allow the removal of all non-existing CTFs.")
    else:
        ctf_dict = state_manager.get_ctf()
        challenges = ctf_dict["challenges"]
        initial_active_challenge= ctf_dict["active_challenge"]
        print_rich(f"{len(challenges)} [blue not bold]challenge{"s" if len(challenges) > 1 or len(challenges) == 0 else ""} found in the active CTF {state_dict['active_ctf']}.[/blue not bold]")
        removed_counter, not_exists_counter = 0, 0
        if len(challenges) > 0:
            with typer.progressbar(challenges.copy(), label=f"Cleaning up challenges in f{state_dict["active_ctf"]}") as progress:
                for name in progress:
                    challenge_directory = Path(ctf_dict["directory"]) / challenges[name]["category"] / name
                    if not challenge_directory.exists():
                        not_exists_counter += 1
                        print_warning(f"\n\nChallenge not found: {name} at {challenge_directory}.")
                        delete_input = typer.confirm(f"Do you want to remove {name} from the challenge list?")
                        if not delete_input:
                            print("Skipping...")
                        else:
                            removed_counter += 1
                            state_manager.remove_challenge(name)
                            print_success(f"{"Deactivated and r" if initial_active_challenge == name else "R"}emoved {name} from the challenge list.")
            
        if removed_counter == 0 and not_exists_counter == 0:
            print_success(f"All challenges in {state_dict['active_ctf']} are valid and existing.", True)
        else:
            print_success(f"Cleanup complete.", True)
            print_info(f"Found {not_exists_counter} non-existing challenge{'s' if not_exists_counter > 1 else ''} and removed {removed_counter} challenge{'s' if removed_counter > 1 or removed_counter == 0 else ''}.", True)
            if not_exists_counter-removed_counter > 0:
                print_warning("It is recommended you allow the removal of all non-existing challenges.")

@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(command_and_args: List[str] = typer.Argument(
        ...,
        help="The command to execute, followed by its arguments. ",
        allow_dash=True
    )):
    """
    Run a command in the current active CTF directory or active challenge directory.
    """
    command = command_and_args[0]
    args = command_and_args[1:] if len(command_and_args) > 1 else []
    ctf_dict = state_manager.get_ctf()
    chal_dict = state_manager.get_chal()
    
    original_cwd = os.getcwd()
    command_cwd = Path(ctf_dict['directory']) / chal_dict['category'] / chal_dict['name']
    
    try:
        result = subprocess.run([command] + args,
                                cwd=command_cwd,
                                check=True,
                                capture_output=True,
                                text=True,
                                shell=False)
        if result.stdout:
            typer.echo(result.stdout)
    except subprocess.CalledProcessError as e:
        print_error(f"[b red]Error: [/b red]: Command '{' '.join(command_and_args)}' failed with exit code {e.returncode}.")
        if e.stdout:
            typer.echo(f"{e.stdout}", err=True)
        if e.stderr:
            typer.echo(f"{e.stderr}", err=True)
        raise typer.Exit(code=e.returncode)
    except Exception as e:
        print_error(f"[b red]Error: [/b red]{e}")
        if ENV == "DEV":
            typer.echo(f"An unexpected error occurred: {e}", err=True)
            raise typer.Exit(code=1)
    finally:
        # Always change back to the original directory
        os.chdir(original_cwd)


if __name__ == "__main__":
    app()