# SPDX-FileCopyrightText: 2025-present Gordon Watts <gwatts@uw.edu>
#
# SPDX-License-Identifier: MIT
"""
Command-line interface for atlas-mc-scanner
"""
import logging
import typer

app = typer.Typer()


def set_verbosity(verbose: int):
    if verbose == 0:
        level = logging.WARNING
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG
    logging.basicConfig(level=level)


@app.command()
def particles(
    data_set_name: str = typer.Argument(..., help="RUCIO dataset name"),
    container: str = typer.Option(
        "TruthBSMWithDecayParticles",
        "--container",
        help="Name of the container to query (default: TruthBSMWithDecayParticles)",
    ),
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        help="Increase verbosity (-v for INFO, -vv for DEBUG)",
    ),
):
    """Dump particles in the dataset."""
    set_verbosity(verbose)
    from atlas_mc_scanner.list_particles import execute_request

    execute_request(data_set_name, container)


@app.command()
def decays(
    data_set_name: str = typer.Argument(..., help="RUCIO dataset name"),
    particle_name: str = typer.Argument(
        ...,
        help="The integer pdgid or the recognized name (25 or e-).",
    ),
    container: str = typer.Option(
        "TruthBSMWithDecayParticles",
        "--container",
        help="Name of the container to query (default: TruthBSMWithDecayParticles)",
    ),
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        help="Increase verbosity (-v for INFO, -vv for DEBUG)",
    ),
):
    """print out decay frequency for a particular particle"""
    set_verbosity(verbose)
    from atlas_mc_scanner.decays import execute_decay

    execute_decay(data_set_name, particle_name, container)


@app.command()
def find_containers(
    data_set_name: str = typer.Argument(..., help="RUCIO dataset name"),
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        help="Increase verbosity (-v for INFO, -vv for DEBUG)",
    ),
):
    """List containers that likely contain TruthParticles."""
    set_verbosity(verbose)
    from atlas_mc_scanner.find_containers import execute_find_containers

    execute_find_containers(data_set_name)


if __name__ == "__main__":
    app()
