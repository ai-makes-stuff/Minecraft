"""Player state and interaction helpers."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from . import blocks
from .world import Coordinate, World

Direction = Tuple[int, int, int]


DIRECTIONS: Dict[str, Direction] = {
    "north": (0, 0, -1),
    "south": (0, 0, 1),
    "east": (1, 0, 0),
    "west": (-1, 0, 0),
    "up": (0, 1, 0),
    "down": (0, -1, 0),
}


@dataclass
class Player:
    """Simple player representation."""

    world: World
    position: Coordinate = field(init=False)
    inventory: Counter = field(default_factory=Counter)

    def __post_init__(self) -> None:
        spawn = self.world.spawn_position()
        self.position = (spawn[0], spawn[1] + 1, spawn[2])
        # Provide a starting kit for building shelters.
        self.inventory.update({"planks": 8})

    # ------------------------------------------------------------------
    # Movement

    def move(self, direction: str) -> bool:
        """Move the player in ``direction`` if possible."""

        if direction not in DIRECTIONS:
            raise ValueError(f"Unknown direction: {direction}")

        dx, dy, dz = DIRECTIONS[direction]
        x, y, z = self.position
        new_position = (x + dx, y + dy, z + dz)

        if direction in {"up", "down"}:
            target_block = self.world.get_block(new_position)
            if target_block.id == "air" or target_block.id == "water":
                self.position = new_position
                return True
            return False

        # Horizontal movement steps to the surface of the destination column.
        dest_x = new_position[0]
        dest_z = new_position[2]
        if not (0 <= dest_x < self.world.bounds.width and 0 <= dest_z < self.world.bounds.depth):
            return False
        dest_y = self.world.column_height(dest_x, dest_z) + 1
        if dest_y >= self.world.bounds.height:
            return False
        self.position = (dest_x, dest_y, dest_z)
        return True

    # ------------------------------------------------------------------
    # Block interaction helpers

    def _target_from_direction(self, direction: Optional[str]) -> Coordinate:
        x, y, z = self.position
        if direction is None:
            direction = "up"
        if direction not in DIRECTIONS:
            raise ValueError(f"Unknown direction: {direction}")
        dx, dy, dz = DIRECTIONS[direction]
        return (x + dx, y + dy, z + dz)

    def harvest(self, direction: Optional[str] = None) -> Optional[str]:
        """Break the block in ``direction`` and add it to the inventory."""

        target = self._target_from_direction(direction)
        block = self.world.get_block(target)
        if block.id in {"air", "water"}:
            return None
        removed = self.world.remove_block(target)
        if removed is None:
            return None
        self.inventory[removed.id] += 1
        return removed.id

    def place(self, block_id: str, direction: Optional[str] = None) -> bool:
        """Place ``block_id`` in ``direction`` if the space is empty."""

        target = self._target_from_direction(direction)
        block_id = block_id.lower()
        if self.inventory.get(block_id, 0) <= 0:
            return False
        existing = self.world.get_block(target)
        if existing.id != "air" and existing.id != "water":
            return False
        placed = self.world.set_block(target, block_id)
        if placed:
            self.inventory[block_id] -= 1
            if self.inventory[block_id] <= 0:
                del self.inventory[block_id]
        return placed

    def craft(self, block_id: str) -> bool:
        """Attempt to craft ``block_id`` using available resources."""

        return blocks.craft(block_id, self.inventory)

    # ------------------------------------------------------------------
    # Presentation helpers

    def describe_surroundings(self) -> str:
        """Return a textual description of nearby blocks."""

        x, y, z = self.position
        head_block = self.world.get_block((x, y, z))
        ground_block = self.world.get_block((x, y - 1, z))
        below_block = self.world.get_block((x, y - 2, z)) if y - 2 >= 0 else blocks.BLOCKS["stone"]
        descriptions = [
            f"You are standing above {ground_block.name.lower()}.",
            f"There is {head_block.name.lower()} at head height.",
            f"Beneath you lies {below_block.name.lower()}.",
        ]
        return " \n".join(descriptions)

    def inventory_summary(self) -> str:
        if not self.inventory:
            return "Your inventory is empty."
        parts = [f"{count} x {blocks.BLOCKS[item].name}" for item, count in sorted(self.inventory.items())]
        return "You carry: " + ", ".join(parts)
