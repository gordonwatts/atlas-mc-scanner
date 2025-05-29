from collections import defaultdict

import awkward as ak
from func_adl_servicex_xaodr25 import FuncADLQueryPHYS
from tabulate import tabulate

from atlas_mc_scanner.common import (
    get_particle_name,
    get_pdgid_from_name_or_int,
    run_query,
)


def query(pdgid: int, container_name="TruthBSMWithDecayParticles"):
    "Build base query for MC particles"
    query_base = FuncADLQueryPHYS()

    # Establish all the various types of objects we need.
    all_mc_particles = query_base.Select(
        lambda e: e.TruthParticles(container_name)
    ).Select(
        lambda particles: particles.Where(lambda p: p.pdgId() == pdgid).Where(
            lambda p: p.hasDecayVtx()
        )
    )

    # Next, fetch everything we want from them.
    result = all_mc_particles.Select(
        lambda e: {
            "decay_pdgId": [
                [vp.pdgId() for vp in t.decayVtx().outgoingParticleLinks()] for t in e
            ]
        }
    )

    return result


def execute_decay(
    data_set_name: str,
    particle_name: str,
    container_name: str = "TruthBSMWithDecayParticles",
):
    """
    Print out decay frequency for a particular particle.

    Args:
        data_set_name (str): The RUCIO dataset name.
        particle_name (str): The integer pdgid or the recognized name (e.g., "25" or "e-").
        container_name (str): The name of the container to query.
    """
    # Convert particle name to pdgid
    pdgid = get_pdgid_from_name_or_int(particle_name)

    # Run the query.
    q = query(pdgid, container_name)
    result = run_query(q, data_set_name)["decay_pdgId"]

    def as_tuple(np_decay):
        "Turn a list of integers into a tuple of integers"
        return tuple(int(a) for a in np_decay)

    # Find all the unique decays. This is horribly slow, but it works.
    # unique, counts = np.unique(
    #     ak.flatten(result).to_numpy(), return_counts=True, axis=0
    # )
    counts_dict = defaultdict(int)
    for decay in ak.flatten(result):
        decay_tuple = as_tuple(decay)
        counts_dict[decay_tuple] += 1

    unique = list(counts_dict.keys())
    counts = list(counts_dict.values())

    decay_names = {
        as_tuple(a_decay): " + ".join(get_particle_name(pid) for pid in list(a_decay))
        for a_decay in unique
    }

    # Print table of decay frequencies

    total = sum(counts)
    table = []
    for decay, count in zip(unique, counts):
        decay_tuple = as_tuple(decay)
        fraction = count / total if total > 0 else 0
        table.append(
            [list(decay_tuple), decay_names[decay_tuple], count, f"{fraction:.2%}"]
        )
    table.sort(key=lambda row: float(row[3].strip("%")), reverse=True)
    print(
        tabulate(
            table,
            headers=["Decay Products (PDGIDs)", "Decay Names", "Frequency", "Fraction"],
            tablefmt="fancy_grid",
        )
    )
