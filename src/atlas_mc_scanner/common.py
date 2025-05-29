import logging
import os
from pathlib import Path
import re
from typing import Tuple
from urllib.parse import unquote, urlparse

try:
    import servicex_local as sx_local
except ImportError:
    # If servicex_local is not available, we will use the remote ServiceX
    sx_local = None

from particle import Particle
from servicex import Sample, ServiceXSpec, dataset, deliver
from servicex_analysis_utils import to_awk


def find_dataset(
    ds_name: str,
) -> Tuple[dataset.FileList | dataset.Rucio | dataset.XRootD, bool]:
    """Use heuristics to determine what it is we are after here.
    This function will return a dataset object that can be used to fetch the data.
    It will try to figure out if the input is a URL, a local file, or a Rucio dataset.

    Args:
        ds_name (str): The name of the dataset to be fetched.

    Returns:
        dataset.FileList | dataset.Rucio | dataset.XRootD: The dataset for ServiceX to use.
        bool: If true, then must run locally. Otherwise run remotely.
    """
    # first, determine what we are looking at.
    what_is_it = None
    if re.match(r"^https?://", ds_name):
        what_is_it = "url"
        url = ds_name

        # Check for the special case of cernbox - which we might be able to convert to
        # a xrootd path.
        parsed_url = urlparse(url)
        if "cernbox.cern.ch" in parsed_url.netloc and parsed_url.path.startswith(
            "/files/spaces"
        ):
            remote_file = f"root://eospublic.cern.ch{parsed_url.path[13:]}"
            what_is_it = "remote_file"

    elif re.match(r"^file://", ds_name):
        # Convert file URI to a path in a cross-platform way

        parsed_uri = urlparse(ds_name)
        file_path = unquote(parsed_uri.path)
        if os.name == "nt" and file_path.startswith("/"):
            file_path = file_path[1:]

        file = Path(file_path).absolute()
        what_is_it = "file"
    elif re.match(r"^rucio://", ds_name):
        what_is_it = "rucio"
        did = ds_name[8:]
    else:
        # Now we need to use heuristics to decide what this is. If you are running
        # on a file that does not exist you'll get a DID error here. Ugh.
        file = Path(ds_name).absolute()
        if file.exists():
            what_is_it = "file"
        else:
            if os.path.sep in ds_name:
                raise ValueError(
                    f"{ds_name} looks like a file path, but the file does not exist"
                )
            did = ds_name
            what_is_it = "rucio"

    if what_is_it == "url":
        logging.debug(f"Interpreting {ds_name} as a url")
        return dataset.FileList([url]), False
    elif what_is_it == "file":
        logging.debug(f"Interpreting {ds_name} as a local file ({file})")
        if file.exists():
            # If ds_name is a local file
            logging.debug(f"Interpreting dataset as local file: {file}")
            return dataset.FileList([str(file)]), True
        else:
            raise ValueError(f"This local file {file} does not exist.")
    elif what_is_it == "remote_file":
        logging.debug(f"Interpreting {ds_name} as a remote file ({remote_file})")
        return dataset.FileList([remote_file]), False
    elif what_is_it == "rucio":
        logging.debug(f"Interpreting {ds_name} as a rucio dataset ({did})")
        return dataset.Rucio(did, num_files=1), False
    else:
        raise RuntimeError(f"Unknown type of input {what_is_it}")


def install_sx_local():
    """
    Set up and register a local ServiceX endpoint for data transformation.

    This function initializes the necessary components for a local ServiceX
    endpoint, including the code generator, science runner, and adaptor.
    It then registers this endpoint with the ServiceX configuration.

    Returns:
        tuple: A tuple containing the names of the codegen and backend.
    """
    if sx_local is None:
        raise ImportError(
            "servicex-local is not installed. Please install it using the `[local]` "
            "option or directly."
        )
    from servicex_local import DockerScienceImage, LocalXAODCodegen, SXLocalAdaptor

    codegen_name = "atlasr22-local"

    codegen = LocalXAODCodegen()
    # science_runner = WSL2ScienceImage("atlas_al9", "25.2.12")
    science_runner = DockerScienceImage(
        "sslhep/servicex_func_adl_xaod_transformer:25.2.41"
    )
    adaptor = SXLocalAdaptor(
        codegen, science_runner, codegen_name, "http://localhost:5001"
    )

    logging.info(f"Using local ServiceX endpoint: codegen {codegen_name}")

    return codegen_name, "local-backend", adaptor


def run_query(query, ds_name: str):
    """Build a ServiceX spec from the given query and dataset."""

    # Assume a ServiceX remote dataset.
    ds, run_local = find_dataset(ds_name)

    adaptor = None
    if run_local:
        codegen_name, backend_name, adaptor = install_sx_local()
    else:
        backend_name = "servicex"
        codegen_name = "atlasr22"

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

    # Get the result
    sx_result = (
        sx_local.deliver(spec, adaptor=adaptor)
        if run_local
        else deliver(spec, servicex_name=backend_name)
    )

    # Turn it into something useful we can process!
    result_list = to_awk(sx_result)["MySample"]
    logging.info(f"Received {len(result_list)} entries.")
    return result_list


def get_particle_name(pdgid):
    try:
        return Particle.from_pdgid(pdgid).name
    except Exception:
        return f"Unknown ({pdgid})"


def get_pdgid_from_name_or_int(particle_name):
    """
    Convert a particle name or PDGID string to an integer PDGID.
    Args:
        particle_name (str): The integer pdgid or the recognized name (e.g., "25" or "e-").
    Returns:
        int: The PDGID as an integer.
    """
    from particle import Particle

    try:
        return int(Particle.from_name(particle_name).pdgid)
    except Exception:
        return int(particle_name)
