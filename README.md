# atlas-mc-scanner

[![PyPI - Version](https://img.shields.io/pypi/v/atlas-mc-scanner.svg)](https://pypi.org/project/atlas-mc-scanner)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/atlas-mc-scanner.svg)](https://pypi.org/project/atlas-mc-scanner)

-----

## Table of Contents

- [Usage](#usage)
- [Installation](#installation)
- [License](#license)

## Usage

**Prerequisites**:

1. [Install the package manager `uv`](https://docs.astral.sh/uv/getting-started/installation/) on your machine.
1. [Get a `servicex.yaml` file](https://servicex-frontend.readthedocs.io/en/stable/connect_servicex.html) in your home directory.
    - As of this writing the UChicago instructions are slightly out of date. After clicking the `sign-in` link at the top of the UChicago `servicex` page, look for the `ATLAS` button. Click that and use your usual CERN sign-on.

The package manager `uv` enables a fast download and isolated install of simple utilities - and it means you don't have to pay attention to dependencies or anything else.

**Running**:

Here is the help you get back:

```bash
PS C:\Users\gordo> uvx atlas-mc-scanner --help
Installed 82 packages in 1.25s

 Usage: atlas-mc-scanner [OPTIONS] COMMAND [ARGS]...

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                                                                                                                                                        │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                                                                                                                                                 │
│ --help                        Show this message and exit.                                                                                                                                                                                                      │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ particles         Dump particles in the dataset.                                                                                                                                                                                                               │
│ decays            print out decay frequency for a particular particle                                                                                                                                                                                          │
│ find-containers   List containers that likely contain TruthParticles.                                                                                                                                                                                          │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Here is an example of a list of particle decays in the default container `TruthBSMWithDecayParticles`:

```bash
PS C:\Users\gordo> uvx atlas-mc-scanner particles mc23_13p6TeV:mc23_13p6TeV.561231.MGPy8EG_A14N23LO_HAHM_ggHZdZd_mumu_600_0p005.deriv.DAOD_LLP1.e8577_e8528_a934_s4370_r16083_r15970_p6619_tid42970882_00

╒══════════╤══════════════╤═════════╤═══════════════════╤═══════════════════╤═══════════════════╕
│   PDG ID │ Name         │   Count │   Avg Count/Event │   Max Count/Event │   Min Count/Event │
╞══════════╪══════════════╪═════════╪═══════════════════╪═══════════════════╪═══════════════════╡
│       13 │ mu-          │   45622 │            4.5622 │                 6 │                 2 │
├──────────┼──────────────┼─────────┼───────────────────┼───────────────────┼───────────────────┤
│       32 │ Unknown (32) │   20000 │            2      │                 2 │                 2 │
├──────────┼──────────────┼─────────┼───────────────────┼───────────────────┼───────────────────┤
│       22 │ gamma        │    2825 │            0.2825 │                 7 │                 0 │
├──────────┼──────────────┼─────────┼───────────────────┼───────────────────┼───────────────────┤
│       11 │ e-           │      25 │            0.0025 │                 4 │                 0 │
╘══════════╧══════════════╧═════════╧═══════════════════╧═══════════════════╧═══════════════════╛
```

### Commands

- Use the `particles` sub-command to list a container of truth particles
- Use the `decays` sub-command to list the decays of a particular particle
- Use the `find-containers` sub-command to list all containers in the file that contains `TruthParticle`s. Note this uses heuristics, so it might not be 100% correct.

All datasets are assumed to be rucio, though you can specify a `https://xxx` for a file if you like. Obviously, they must be a file in the `xAOD` format! This code uses the `EventLoop` C++ framework, run on ServiceX to extract the information.

## Installation

```console
pip install atlas-mc-scanner
```

## License

`atlas-mc-scanner` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
