import logging

import awkward as ak
import numpy as np
from func_adl import ObjectStream
from func_adl_servicex_xaodr25 import FuncADLQueryPHYS
from servicex import Sample, ServiceXSpec, dataset, deliver
from servicex_analysis_utils import to_awk
from tabulate import tabulate
from particle import Particle


def query():
    "Build base query for MC particles"
    query_base = FuncADLQueryPHYS()

    # Establish all the various types of objects we need.
    all_mc_particles = query_base.Select(
        lambda e: e.TruthParticles("TruthBSMWithDecayParticles")
    )

    # Next, fetch everything we want from them.
    result = all_mc_particles.Select(lambda e: {"pdgid": [t.pdgId() for t in e]})

    return result


def build_sx_spec(query, ds_name: str):
    """Build a ServiceX spec from the given query and dataset."""

    # Assume a ServiceX remote dataset.
    ds = dataset.Rucio(ds_name, num_files=1)

    # backend_name = "af.uchicago"
    codegen_name = "atlasr22"
    backend_name = "servicex"

    # Build the ServiceX spec
    spec = ServiceXSpec(
        Sample=[
            Sample(
                Name="MySample",
                Dataset=ds,
                Query=query,
                Codegen=codegen_name,
            ),
        ],
    )

    return spec, backend_name


def run_query(
    ds_name: str,
    query: ObjectStream,
) -> ak.Array:
    # Build the ServiceX spec and run it.
    spec, backend_name = build_sx_spec(query, ds_name)

    sx_result = deliver(spec, servicex_name=backend_name)

    result_list = to_awk(sx_result)["MySample"]
    logging.info(f"Received {len(result_list)} entries.")
    return result_list


def get_particle_name(pdgid):
    try:
        return Particle.from_pdgid(pdgid).name
    except Exception:
        return f"Unknown ({pdgid})"


def execute_request(ds_name):
    q = query()
    result = run_query(ds_name, q)

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
            pid,
            get_particle_name(pid),
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
