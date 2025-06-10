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

And looking at the decay products:

```bash
$ atlas-mc-scanner decays mc23_13p6TeV:mc23_13p6TeV.561231.MGPy8EG_A14N23LO_HAHM_ggHZdZd_mumu_600_0p005.deriv.DAOD_LLP1.e8577_e8528_a934_s4370_r16083_r15970_p6619_tid42970882_00 13

╒═══════════════════════════╤═══════════════╤═════════════╤════════════╕
│ Decay Products (PDGIDs)   │ Decay Names   │   Frequency │ Fraction   │
╞═══════════════════════════╪═══════════════╪═════════════╪════════════╡
│ [13, 22]                  │ mu- + gamma   │        1438 │ 40.66%     │
├───────────────────────────┼───────────────┼─────────────┼────────────┤
│ [13]                      │ mu-           │        1373 │ 38.82%     │
├───────────────────────────┼───────────────┼─────────────┼────────────┤
│ No Decay Products         │               │         726 │ 20.53%     │
╘═══════════════════════════╧═══════════════╧═════════════╧════════════╛
```

The ATLAS decay model is complex:

- If the _Decay Products_ column contains `No Decay Products`, that means a decay vertex was found in the `TruthParticle`, but it had decay products.
- If the _Decay Products_ column contains `Stable`, that means no decay vertex was found.

### Commands

- Use the `particles` sub-command to list a container of truth particles
- Use the `decays` sub-command to list the decays of a particular particle
- Use the `find-containers` sub-command to list all containers in the file that contains `TruthParticle`s. Note this uses heuristics, so it might not be 100% correct.

All datasets are assumed to be rucio, though you can specify a `https://xxx` for a file if you like. Obviously, they must be a file in the `xAOD` format! This code uses the `EventLoop` C++ framework, run on ServiceX to extract the information.

## Errors

Some common errors you might see.

### Missing `servicex.yaml` file

The error message when you run is fairly straight forward. The `servicex.yaml` file (or `.servicex`) must exist in your home directory or in the current working directory.

### Your dataset does not exist

This is a known [bug](https://github.com/gordonwatts/atlas-mc-scanner/issues/22). There are two hints. First, the `Transform` status update will be _red_ rather than _green_. Second, you'll have a stack dump that ends with the message `IndexError: list index out of range`.

### Bad container name

You will get the same stack-dump as with the data set not existing (the `list index out of range`), and scroll up and look at the top of the crash and look for `Transform "atlas-mc-scanner" completed with failures: 1/1`. Below that will be a huge URL which points to the monitoring (it is the seocond URL in the dump). From there look for an `ERROR` and click on the second column to expand that error entry. There, under `logBody` you can see the complete output from the EventLoop job. Near the bottom you'll finally find the familiar errors:

```text
xAOD::TEvent::connectB... WARNING No metadata available for branch: forkitover
xAOD::TEvent::connectB... WARNING Branch "forkitover" not available on input
xAOD::TEvent::retrieve    WARNING Couldn't (const) retrieve "DataVector<xAOD::TruthParticle_v1>/forkitover"
AnalysisAlg              ERROR   /home/atlas/rel/source/analysis/Root/query.cxx:73 (virtual StatusCode query::execute()): Failed to call "evtStore()->retrieve(result, "forkitover")"
```

## Installation

```console
pip install atlas-mc-scanner
```

## License

`atlas-mc-scanner` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
