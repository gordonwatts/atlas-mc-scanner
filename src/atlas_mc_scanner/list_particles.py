import awkward as ak
import numpy as np
from dataclasses import dataclass
from typing import List

from func_adl_servicex_xaodr25 import FuncADLQueryPHYS

from atlas_mc_scanner.common import run_query, get_particle_name


@dataclass
class ParticleSummary:
    """Summary information for a particular particle id."""

    pdgid: int
    name: str
    count: int
    avg_per_event: float
    max_per_event: int
    min_per_event: int


def query(container_name="TruthBSMWithDecayParticles"):
    "Build base query for MC particles"
    query_base = FuncADLQueryPHYS()

    # Establish all the various types of objects we need.
    all_mc_particles = query_base.Select(lambda e: e.TruthParticles(container_name))

    # Next, fetch everything we want from them.
    result = all_mc_particles.Select(lambda e: {"pdgid": [t.pdgId() for t in e]})

    return result


def summarize_particles(
    ds_name: str,
    container_name: str = "TruthBSMWithDecayParticles",
    no_abs: bool = False,
) -> List[ParticleSummary]:
    """Return a summary of particles found in the dataset."""

    q = query(container_name)
    result = run_query(q, ds_name)

    # now, collate everything by particle id to get a count.
    total_events = len(result)

    pdgid_list = result.pdgid if no_abs else abs(result.pdgid)
    r = ak.flatten(pdgid_list).to_numpy()

    unique, counts = np.unique(r, return_counts=True)
    pdgid_counts = dict(zip(unique, counts))

    # Lets calculate the max and min particle counts for each particle id.
    count = {pid: ak.count(result.pdgid[result.pdgid == pid], axis=1) for pid in unique}
    max_count = {pid: ak.max(count[pid]) for pid in unique}
    min_count = {pid: ak.min(count[pid]) for pid in unique}

    summaries = [
        ParticleSummary(
            pdgid=int(pid),
            name=get_particle_name(int(pid)),
            count=count,
            avg_per_event=count / total_events,
            max_per_event=int(max_count[pid]),
            min_per_event=int(min_count[pid]),
        )
        for pid, count in pdgid_counts.items()
    ]

    summaries.sort(key=lambda s: s.count, reverse=True)
    return summaries
