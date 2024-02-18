from click_aliases import ClickAliasedGroup
from prettytable import PrettyTable
from typing import Tuple

import palimpzest as pz

import click
import os
import subprocess
import yaml

############ DEFINITIONS ############
PZ_DIR = os.path.join(os.path.expanduser("~"), ".palimpzest")

class InvalidCommandException(Exception):
    pass


############## HELPERS ##############
def _print_msg(msg: str) -> None:
    """
    Helper function to print messages in CLI-specific format. Currently just a wrapper around print(),
    could easily be extended to include color/formatted output.

    Parameters
    ----------
    msg: str
        Message to print to the console.
    """
    # TODO: use colorama for different color outputs to improve readability
    print(f"{msg}")


def _run_bash_command(command: str) -> Tuple[str, str]:
    """
    Helper function to split a bash command on spaces and execute it using subprocess.

    Parameters
    ----------
    command: str
        Shell command to execute with subprocess.

    Returns
    -------
    Tuple[str, str]
        Tuple returning the stdout and stderr from running the shell command.
    """
    # split command on spaces into list of strings
    command_str_lst = command.split(" ")

    # execute command and capture the output
    out = subprocess.run(command_str_lst, capture_output=True)

    # return stdout as string
    return str(out.stdout, "utf-8"), str(out.stderr, "utf-8")


def _help() -> str:
    """
    Syntactic sugar to call `pz --help` when a user calls `pz help`.

    Returns
    -------
    str
        The help text for the pz CLI.
    """
    # execute the help command using subprocess and return output
    stdout, _ = _run_bash_command("pz --help")

    return stdout


############ CLICK API ##############
@click.group(cls=ClickAliasedGroup)
def cli():
    """
    The CLI tool for Palimpzest.
    """
    pass


@cli.command(aliases=["h"])
def help() -> None:
    """
    Print the help message for PZ.
    """
    _print_msg(_help())


@cli.command(aliases=["i"])
def init() -> None:
    """
    Initialize data directory for PZ.
    """
    # set directory and initialize it for PZ
    pz.DataDirectory()
    _print_msg(f"Palimpzest system initialized in: {PZ_DIR}")


@cli.command(aliases=["lsdata", "ls"])
def ls_data() -> None:
    """
    Print a table listing the datasets registered with PZ.
    """
    # fetch list of registered datasets
    ds = pz.DataDirectory().listRegisteredDatasets()

    # construct table for printing
    table = [["Name", "Type", "Path"]]
    for path, descriptor in ds:
        table.append([path, descriptor[0], descriptor[1]])

    # print table of registered datasets
    t = PrettyTable(table[0])
    t.add_rows(table[1:])
    _print_msg(t)
    _print_msg("")
    _print_msg(f"Total datasets: {len(table) - 1}")


@cli.command(aliases=["register", "reg", "r"])
@click.option("--path", type=str, default=None, help="File or directory to register as dataset.")
@click.option("--name", type=str, default=None, help="Registered name for the file/dir.")
def register_data(path: str, name: str) -> None:
    """
    Register a data file or data directory with PZ.

    Parameters
    ----------
    path: str
        Path to the data file or directory to register with PZ.

    name: str
        Name to register the data file / directory with.
    """
    # parse path and name; enforce that user provides them
    if path is not None and name is not None:
        path = path.strip()
        name = name.strip()
    else:
        raise InvalidCommandException(
            f"Please provide a name for the data file/dir. using --name"
        )

    # register dataset
    if os.path.isfile(path):     
        pz.DataDirectory().registerLocalFile(os.path.abspath(path), name)

    elif os.path.isdir(path):
        pz.DataDirectory().registerLocalDirectory(os.path.abspath(path), name)

    else:
        raise InvalidCommandException(
            f"Path {path} is invalid. Does not point to a file or directory."
        )

    _print_msg(f"Registered {name}")


@cli.command(aliases=["rmdata", "rm"])
@click.option("--name", type=str, default=None, help="Name of registered dataset to be removed.")
def rm_data(name: str) -> None:
    """
    Remove a dataset that was registered with PZ.

    Parameters
    ----------
    name: str
        Name of the dataset to unregister.
    """
    # parse name and enforce that user provides it
    if name is not None:
        name = name.strip()
    else:
        raise InvalidCommandException(
            f"Please provide a name for the registered dataset using --name"
        )

    # remove dataset from registry
    pz.DataDirectory().rmRegisteredDataset(name)

    _print_msg(f"Deleted {name}")


@cli.command(aliases=["config", "pc"])
def print_config() -> None:
    """
    Print the current config that Palimpzest is using.
    """
    # load config yaml file
    config = pz.DataDirectory().getConfig()

    # print contents of config
    _print_msg(f"--- {config['name']} ---\n{yaml.dump(config)}")


@cli.command(aliases=["cc"])
def create_config() -> None:
    """
    Create a Palimpzest config. You must set the following fields:

    TODO
    """
    # TODO
    pass


@cli.command(aliases=["rmconfig", "rmc"])
def rm_config() -> None:
    """
    Remove the specified config from Palimpzest.

    TODO
    """
    # TODO
    pass


@cli.command(aliases=["set", "sc"])
def set_config() -> None:
    """
    Set the current config for Palimpzest to use.

    TODO
    """
    # TODO
    pass


def main():
    """
    Entrypoint for Palimpzest CLI tool implemented using Click.
    """
    cli.add_command(help)
    cli.add_command(init)
    cli.add_command(ls_data)
    cli.add_command(register_data)
    cli.add_command(rm_data)
    cli.add_command(print_config)
    cli.add_command(create_config)
    cli.add_command(rm_config)
    cli.add_command(set_config)
    cli()
