"""Module to interact with aa-eveprices"""

from typing import Set

from eveprices.models import TypePrice

from eveuniverse.models import EveGroup, EveType

MOON_GOOS_GROUP_ID = 427
FUEL_BLOCK_GROUP_ID = 1136
MAGMATIC_TYPE_ID = 81143


def get_eve_type_price(eve_type: EveType) -> float:
    """Get the price of an eve type"""
    return get_eve_type_id_price(eve_type.id)


def get_eve_type_id_price(eve_type_id: int) -> float:
    """Returns the price of an item id"""
    return TypePrice.objects.get_price_immediate(eve_type_id)


def get_type_ids_from_group(group_id: int) -> Set[int]:
    """Fetches type ids from their group and returns it as a set"""
    group = EveGroup.objects.get(id=group_id)
    return set(group.eve_types.filter(published=True).values_list("id", flat=True))


def get_fuels_type_ids() -> Set[int]:
    """Fetches the id of all 4 fuel blocks from their group and magmatic gas"""
    return get_type_ids_from_group(FUEL_BLOCK_GROUP_ID) | {MAGMATIC_TYPE_ID}


def get_fuel_blocs_type_ids() -> Set[int]:
    """Fetches the id of all 4 fuel blocks"""
    return get_type_ids_from_group(FUEL_BLOCK_GROUP_ID)


def get_moon_goos_type_ids() -> Set[int]:
    """Fetches the ids of all moon goos from their group"""
    return get_type_ids_from_group(MOON_GOOS_GROUP_ID)


def get_fuel_block_price() -> float:
    """Returns the price of the cheapest fuel block"""
    min_price = 10e25
    for fuel_type_id in get_fuel_blocs_type_ids():
        fuel_price = TypePrice.objects.get_price_immediate(fuel_type_id)
        min_price = min(fuel_price, min_price)
    return min_price


def get_magmatic_gases_price() -> float:
    """Returns the price of a unit of magmatic gases"""
    return TypePrice.objects.get_price_immediate(MAGMATIC_TYPE_ID)
