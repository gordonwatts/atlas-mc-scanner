from func_adl_servicex_xaodr25 import FuncADLQueryPHYS
from particle import Particle

from atlas_mc_scanner.common import run_query


def query(pdgid: int):
    "Build base query for MC particles"
    query_base = FuncADLQueryPHYS()

    # Establish all the various types of objects we need.
    all_mc_particles = query_base.Select(
        lambda e: e.TruthParticles("TruthBSMWithDecayParticles")
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
):
    """
    Print out decay frequency for a particular particle.

    Args:
        data_set_name (str): The RUCIO dataset name.
        particle_name (str): The integer pdgid or the recognized name (e.g., "25" or "e-").
    """
    # Convert particle name to pdgid
    try:
        pdgid = Particle.from_name(particle_name).pdgid
    except Exception:
        pdgid = int(particle_name)

    # Run the query.
    q = query(pdgid)
    result = run_query(data_set_name, q)

    print(result)
