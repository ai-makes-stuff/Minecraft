"""Definitions for the different block types used in the sandbox."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Block:
    """Representation of a block type.

    Parameters
    ----------
    id:
        The identifier used internally.
    name:
        Human friendly name of the block.
    hardness:
        Rough approximation of how hard the block is to break.
    solid:
        Whether the block blocks movement.
    description:
        Short blurb describing the block.
    """

    id: str
    name: str
    hardness: float
    solid: bool = True
    description: str = ""

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


BLOCKS: Dict[str, Block] = {
    "air": Block("air", "Air", hardness=0.0, solid=False, description="Empty space."),
    "grass": Block(
        "grass",
        "Grass",
        hardness=0.6,
        description="Soft topsoil covered with fresh grass.",
    ),
    "dirt": Block(
        "dirt",
        "Dirt",
        hardness=0.5,
        description="Soil that is easy to dig through.",
    ),
    "stone": Block(
        "stone",
        "Stone",
        hardness=1.5,
        description="Solid rock deep below the surface.",
    ),
    "water": Block(
        "water",
        "Water",
        hardness=100.0,
        solid=False,
        description="A splash of refreshing water.",
    ),
    "sand": Block(
        "sand",
        "Sand",
        hardness=0.4,
        description="Grains of crushed stone gathered near the shore.",
    ),
    "log": Block(
        "log",
        "Oak Log",
        hardness=1.0,
        description="A sturdy log that can be turned into planks.",
    ),
    "leaves": Block(
        "leaves",
        "Oak Leaves",
        hardness=0.2,
        solid=False,
        description="Foliage rustling in the wind.",
    ),
    "planks": Block(
        "planks",
        "Oak Planks",
        hardness=1.2,
        description="Refined wood boards perfect for building shelters.",
    ),
}


def get_block(block_id: str) -> Block:
    """Return the :class:`Block` instance for ``block_id``.

    Parameters
    ----------
    block_id:
        Identifier of the block to fetch. The lookup is case-insensitive.

    Raises
    ------
    KeyError
        If the requested block identifier is not known.
    """

    normalized = block_id.lower()
    if normalized not in BLOCKS:
        raise KeyError(f"Unknown block type: {block_id!r}")
    return BLOCKS[normalized]


CRAFTING_RECIPES = {
    "planks": {"log": 1},
}


def can_craft(block_id: str, inventory: Dict[str, int]) -> bool:
    """Return whether the ``inventory`` contains enough resources to craft ``block_id``."""

    recipe = CRAFTING_RECIPES.get(block_id)
    if recipe is None:
        return False
    return all(inventory.get(item, 0) >= count for item, count in recipe.items())


def craft(block_id: str, inventory: Dict[str, int]) -> bool:
    """Attempt to craft ``block_id`` using the provided ``inventory``.

    The function mutates ``inventory`` in place and returns ``True`` on success.
    """

    recipe = CRAFTING_RECIPES.get(block_id)
    if recipe is None:
        return False
    if not can_craft(block_id, inventory):
        return False
    for item, count in recipe.items():
        inventory[item] -= count
        if inventory[item] <= 0:
            inventory.pop(item)
    inventory[block_id] = inventory.get(block_id, 0) + 4 if block_id == "planks" else inventory.get(block_id, 0) + 1
    return True
