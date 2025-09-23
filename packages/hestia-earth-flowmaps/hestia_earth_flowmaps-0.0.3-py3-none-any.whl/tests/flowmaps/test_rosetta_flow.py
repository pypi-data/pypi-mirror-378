from tests.utils import flowmaps_folder
from hestia_earth.flowmaps.RosettaFlow import FlowMap, pick_best_match

ACCEPTABLE_SIMAPRO_DATA_LIBRARY_ECOINVENT_SYSTEM_MODELS = [
    "Ecoinvent 3 - allocation, cut-off by classification - unit",
    "Agribalyse 3.1",
    "AGRIBALYSE - unit",
    "ecoinvent 3.11 (APOS)"
]


def test_ecoinvent():
    map_obj = FlowMap(flowmaps_folder)
    results = map_obj.map_flow(
        {"id": 'electricity, high voltage, electricity production, oil'},
        check_reverse=True,
        search_indirect_mappings=False,
        source_nomenclatures=["ecoinvent_hestia_process"],
        target_nomenclature=ACCEPTABLE_SIMAPRO_DATA_LIBRARY_ECOINVENT_SYSTEM_MODELS,
    )
    assert len(results) == 1

    ecoinvent_processes_candidate = pick_best_match(
        results,
        prefer_unit='kWh',
        preferred_list_names=ACCEPTABLE_SIMAPRO_DATA_LIBRARY_ECOINVENT_SYSTEM_MODELS,
    )
    assert ecoinvent_processes_candidate.Mapper == 'HESTIA'
