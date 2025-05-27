# SPDX-FileCopyrightText: 2025-present Gordon Watts <gwatts@uw.edu>
#
# SPDX-License-Identifier: MIT
"""
Command-line interface for atlas-mc-scanner
"""
import typer

app = typer.Typer()


@app.command()
def particles(data_set_name: str = typer.Argument(..., help="RUCIO dataset name")):
    """Dump particles in the dataset."""
    from atlas_mc_scanner.list_particles import execute_request

    execute_request(data_set_name)


@app.command()
def decays(
    data_set_name: str = typer.Argument(..., help="RUCIO dataset name"),
    particle_name: str = typer.Argument(
        ...,
        help="The integer pdgid or the recognized name (25 or e-).",
    ),
):
    """print out decay frequency for a particular particle"""
    from atlas_mc_scanner.decays import execute_decay

    execute_decay(data_set_name, particle_name)


if __name__ == "__main__":
    app()
