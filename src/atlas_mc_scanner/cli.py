# SPDX-FileCopyrightText: 2025-present Gordon Watts <gwatts@uw.edu>
#
# SPDX-License-Identifier: MIT
"""
Command-line interface for atlas-mc-scanner
"""
import logging
from tabulate import tabulate
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
    no_abs: bool = typer.Option(
        False,
        "--no-abs",
        help="Do not take the absolute value of the pdgid before creating the table.",
    ),
):
    """Dump particles in the dataset."""
    set_verbosity(verbose)
    from atlas_mc_scanner.list_particles import summarize_particles

    summaries = summarize_particles(data_set_name, container, no_abs)
    table = [
        (
            f"{s.pdgid:d}" if no_abs else f"{abs(s.pdgid):d}",
            s.name,
            s.count,
            s.avg_per_event,
            s.max_per_event,
            s.min_per_event,
        )
        for s in summaries
    ]
    print(
        tabulate(
            table,
            headers=[
                "PDG ID" if no_abs else "abs(PDG ID)",
                "Name",
                "Count",
                "Avg Count/Event",
                "Max Count/Event",
                "Min Count/Event",
            ],
            tablefmt="fancy_grid",
        )
    )


@app.command(
    epilog="""
Note:

    - `No Decay Products` means that a `TruthParticle` decay vertex was found, but it had no
       outgoing particles.

    - `Stable` means no decay vertex was found.
"""
)
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
    """Print out decay frequency for a particular particle."""
    set_verbosity(verbose)
    from atlas_mc_scanner.decays import execute_decay

    summaries = execute_decay(data_set_name, particle_name, container)
    table = []
    for s in summaries:
        if s.pdgids is None:
            decay_products = "Stable"
        elif len(s.pdgids) == 0:
            decay_products = "No Decay Products"
        else:
            decay_products = list(s.pdgids)
        table.append(
            [
                decay_products,
                s.decay_names,
                s.count,
                f"{s.fraction:.2%}",
            ]
        )
    print(
        tabulate(
            table,
            headers=["Decay Products (PDGIDs)", "Decay Names", "Frequency", "Fraction"],
            tablefmt="fancy_grid",
        )
    )


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

    containers = execute_find_containers(data_set_name)
    table = [[c.name] for c in containers]
    print(
        tabulate(
            table,
            headers=["Container Name"],
            tablefmt="fancy_grid",
        )
    )


if __name__ == "__main__":
    app()
