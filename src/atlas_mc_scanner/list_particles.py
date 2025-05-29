import awkward as ak
import numpy as np
from func_adl_servicex_xaodr25 import FuncADLQueryPHYS
from tabulate import tabulate

from atlas_mc_scanner.common import run_query, get_particle_name


def query(container_name="TruthBSMWithDecayParticles"):
    "Build base query for MC particles"
    query_base = FuncADLQueryPHYS()

    # Establish all the various types of objects we need.
    all_mc_particles = query_base.Select(lambda e: e.TruthParticles(container_name))

    # Next, fetch everything we want from them.
    result = all_mc_particles.Select(lambda e: {"pdgid": [t.pdgId() for t in e]})

    return result


def execute_request(ds_name, container_name="TruthBSMWithDecayParticles"):
    q = query(container_name)
    result = run_query(q, ds_name)

    # now, collate everything by particle id to get a count.
    total_events = len(result)

    r = ak.flatten(abs(result.pdgid)).to_numpy()

    unique, counts = np.unique(r, return_counts=True)
    pdgid_counts = dict(zip(unique, counts))

    # Lets calculate the max and min particle counts for each particle id.
    count = {pid: ak.count(result.pdgid[result.pdgid == pid], axis=1) for pid in unique}
    max_count = {pid: ak.max(count[pid]) for pid in unique}
    min_count = {pid: ak.min(count[pid]) for pid in unique}

    # Build and print final table.
    table = [
        (
            f"{int(pid):d}",
            get_particle_name(int(pid)),
            count,
            count / total_events,
            max_count[pid],
            min_count[pid],
        )
        for pid, count in pdgid_counts.items()
    ]
    table.sort(key=lambda x: x[2], reverse=True)
    print(
        tabulate(
            table,
            headers=[
                "PDG ID",
                "Name",
                "Count",
                "Avg Count/Event",
                "Max Count/Event",
                "Min Count/Event",
            ],
            tablefmt="fancy_grid",
        )
    )
