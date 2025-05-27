# SPDX-FileCopyrightText: 2025-present Gordon Watts <gwatts@uw.edu>
#
# SPDX-License-Identifier: MIT
"""
Command-line interface for atlas-mc-scanner
"""
import typer

app = typer.Typer()


@app.command()
def particles(data_set_name: str):
    """Dump particles in the dataset."""
    print(data_set_name)


if __name__ == "__main__":
    app()
