import logging

import awkward as ak
from func_adl import ObjectStream
from servicex import Sample, ServiceXSpec, dataset, deliver
from servicex_analysis_utils import to_awk


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
