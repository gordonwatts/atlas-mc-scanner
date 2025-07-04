from collections import defaultdict
from dataclasses import dataclass
from typing import List, Optional, Tuple

import awkward as ak
from func_adl_servicex_xaodr25 import FuncADLQueryPHYS

from atlas_mc_scanner.common import (
    get_particle_name,
    get_pdgid_from_name_or_int,
    run_query,
)


@dataclass
class DecaySummary:
    """Summary information for a particular decay mode."""

    pdgids: Optional[Tuple[int, ...]]
    decay_names: str
    count: int
    fraction: float


def query(pdgid: int, container_name="TruthBSMWithDecayParticles"):
    "Build base query for MC particles"
    query_base = FuncADLQueryPHYS()

    # Establish all the various types of objects we need.
    all_mc_particles = query_base.Select(
        lambda e: e.TruthParticles(container_name)
    ).Select(
        lambda particles: {
            "good": particles.Where(lambda p: p.pdgId() == pdgid).Where(
                lambda p: p.hasDecayVtx()
            ),
            "none_count": particles.Where(lambda p: p.pdgId() == pdgid)
            .Where(lambda p: not p.hasDecayVtx())
            .Count(),
        }
    )

    # Next, fetch everything we want from them.
    result = all_mc_particles.Select(
        lambda e: {
            "decay_pdgId": [
                [vp.pdgId() for vp in t.decayVtx().outgoingParticleLinks()]
                for t in e.good  # type: ignore
            ],
            "none_count": e.none_count,  # type: ignore
        }
    )

    return result


def execute_decay(
    data_set_name: str,
    particle_name: str,
    container_name: str = "TruthBSMWithDecayParticles",
) -> List[DecaySummary]:
    """Return decay frequencies for a particular particle.

    Args:
        data_set_name: The RUCIO dataset name.
        particle_name: The integer pdgid or the recognized name (25 or e-).
        container_name: The name of the container to query.
    """
    # Convert particle name to pdgid
    pdgid = get_pdgid_from_name_or_int(particle_name)

    # Run the query.
    q = query(pdgid, container_name)
    all_results = run_query(q, data_set_name)
    result = all_results["decay_pdgId"]
    none_count = all_results["none_count"]

    def as_tuple(np_decay):
        "Turn a list of integers into a tuple of integers"
        return tuple(int(a) for a in np_decay)

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

    # Build dataclass list of decay frequencies

    total_none_count = ak.sum(none_count)
    total = sum(counts) + total_none_count
    summaries: List[DecaySummary] = []

    for decay, count in zip(unique, counts):
        decay_tuple = as_tuple(decay)
        fraction = count / total if total > 0 else 0.0
        pdgids: Tuple[int, ...] | None = tuple(decay_tuple)
        if len(decay_tuple) == 0:
            pdgids = tuple()
        summaries.append(
            DecaySummary(
                pdgids=pdgids,
                decay_names=decay_names[decay_tuple],
                count=count,
                fraction=float(fraction),
            )
        )

    if total_none_count > 0:
        summaries.append(
            DecaySummary(
                pdgids=None,
                decay_names="",
                count=int(total_none_count),
                fraction=float(total_none_count / total) if total > 0 else 0.0,
            )
        )

    summaries.sort(key=lambda s: s.fraction, reverse=True)

    return summaries
