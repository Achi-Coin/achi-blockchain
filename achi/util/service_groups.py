from typing import KeysView, Generator

SERVICES_FOR_GROUP = {
    "all": "achi_harvester achi_timelord_launcher achi_timelord achi_farmer achi_full_node achi_wallet".split(),
    "node": "achi_full_node".split(),
    "harvester": "achi_harvester".split(),
    "farmer": "achi_harvester achi_farmer achi_full_node achi_wallet".split(),
    "farmer-no-wallet": "achi_harvester achi_farmer achi_full_node".split(),
    "farmer-only": "achi_farmer".split(),
    "timelord": "achi_timelord_launcher achi_timelord achi_full_node".split(),
    "timelord-only": "achi_timelord".split(),
    "timelord-launcher-only": "achi_timelord_launcher".split(),
    "wallet": "achi_wallet achi_full_node".split(),
    "wallet-only": "achi_wallet".split(),
    "introducer": "achi_introducer".split(),
    "simulator": "achi_full_node_simulator".split(),
}


def all_groups() -> KeysView[str]:
    return SERVICES_FOR_GROUP.keys()


def services_for_groups(groups) -> Generator[str, None, None]:
    for group in groups:
        for service in SERVICES_FOR_GROUP[group]:
            yield service


def validate_service(service: str) -> bool:
    return any(service in _ for _ in SERVICES_FOR_GROUP.values())
