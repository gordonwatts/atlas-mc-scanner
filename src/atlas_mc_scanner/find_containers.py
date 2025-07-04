from dataclasses import dataclass
import re
from typing import List

from servicex_analysis_utils import get_structure


@dataclass
class ContainerInfo:
    """Information about a container that likely holds TruthParticles."""

    name: str


def execute_find_containers(data_set_name: str) -> List[ContainerInfo]:
    """Return containers that likely contain TruthParticles for the given dataset name."""

    data = get_structure(data_set_name, array_out=False)
    assert isinstance(data, str), "Expected data to be a string"

    possible_types = [line for line in data.split("\n") if ".pdgId" in line]
    container_names = []
    for line in possible_types:
        match = re.search(r"(\w+)AuxDyn\.pdgId", line)
        if match:
            container_names.append(match.group(1))
    # container_names now contains the parsed names, e.g., ['TruthBSM', ...]

    return sorted(
        [ContainerInfo(name=n) for n in container_names], key=lambda x: x.name
    )
