"""Procedural world generation and manipulation helpers."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, Optional, Tuple

from .blocks import BLOCKS, Block

Coordinate = Tuple[int, int, int]


@dataclass(frozen=True)
class Bounds:
    width: int
    depth: int
    height: int

    def contains(self, position: Coordinate) -> bool:
        x, y, z = position
        return 0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.depth


class World:
    """A small procedurally generated voxel world."""

    def __init__(
        self,
        width: int = 32,
        depth: int = 32,
        height: int = 32,
        *,
        seed: Optional[int] = None,
    ) -> None:
        if width <= 0 or depth <= 0 or height <= 4:
            raise ValueError("World dimensions must be positive with height > 4")
        self.bounds = Bounds(width, depth, height)
        self.seed = seed if seed is not None else random.randint(0, 2**31 - 1)
        self.random = random.Random(self.seed)
        self.sea_level = height // 3 + 2
        self._blocks: Dict[Coordinate, Block] = {}
        self._generate_world()

    # ------------------------------------------------------------------
    # Generation helpers

    def _generate_world(self) -> None:
        for x in range(self.bounds.width):
            for z in range(self.bounds.depth):
                column_height = self._compute_surface_height(x, z)
                column_height = max(1, min(self.bounds.height - 2, column_height))
                for y in range(column_height + 1):
                    if y == column_height:
                        block_id = "grass" if column_height >= self.sea_level else "sand"
                    elif y >= column_height - 3:
                        block_id = "dirt"
                    else:
                        block_id = "stone"
                    self._blocks[(x, y, z)] = BLOCKS[block_id]

                # Fill the column with water if below the sea level.
                if column_height < self.sea_level:
                    for y in range(column_height + 1, self.sea_level + 1):
                        if y < self.bounds.height:
                            self._blocks[(x, y, z)] = BLOCKS["water"]

                # Plant the occasional tree.
                if (
                    column_height >= self.sea_level
                    and column_height + 5 < self.bounds.height
                    and self._tree_rng(x, z) < 0.05
                ):
                    self._grow_tree((x, column_height + 1, z))

    def _tree_rng(self, x: int, z: int) -> float:
        tree_random = random.Random((x * 341873128712 + z * 132897987541 + self.seed) & 0xFFFFFFFF)
        return tree_random.random()

    def _grow_tree(self, trunk_base: Coordinate) -> None:
        x, y, z = trunk_base
        for offset in range(4):
            self._blocks[(x, y + offset, z)] = BLOCKS["log"]
        leaf_positions = [
            (x + dx, y + 3 + dy, z + dz)
            for dx in range(-2, 3)
            for dy in range(-1, 2)
            for dz in range(-2, 3)
            if abs(dx) + abs(dy) + abs(dz) <= 4
        ]
        for pos in leaf_positions:
            if self.bounds.contains(pos):
                self._blocks[pos] = BLOCKS["leaves"]

    def _compute_surface_height(self, x: int, z: int) -> int:
        # Coarse ridges using sine waves.
        ridge = math.sin((x + self.seed) * 0.25) + math.cos((z - self.seed) * 0.3)
        # Small local variance using a deterministic RNG per column.
        column_rng = random.Random((x * 49632) ^ (z * 325176) ^ self.seed)
        jitter = column_rng.uniform(-1.5, 1.5)
        height = int(self.sea_level + ridge * 1.5 + jitter)
        return height

    # ------------------------------------------------------------------
    # Public API

    def spawn_position(self) -> Coordinate:
        """Return a solid spawn position close to the center of the map."""

        center_x = self.bounds.width // 2
        center_z = self.bounds.depth // 2
        return (center_x, self.column_height(center_x, center_z), center_z)

    def column_height(self, x: int, z: int) -> int:
        """Return the highest non-air block for the column at ``(x, z)``."""

        for y in range(self.bounds.height - 1, -1, -1):
            block = self._blocks.get((x, y, z))
            if block and block.id != "air" and block.id != "water":
                return y
        return 0

    def get_block(self, position: Coordinate) -> Block:
        """Return the block located at ``position``.

        Positions outside the world bounds are treated as stone to avoid
        players walking outside the world.
        """

        if not self.bounds.contains(position):
            return BLOCKS["stone"]
        return self._blocks.get(position, BLOCKS["air"])

    def set_block(self, position: Coordinate, block_id: str) -> bool:
        """Place ``block_id`` at ``position`` if inside bounds.

        Returns ``True`` if the block was placed.
        """

        if not self.bounds.contains(position):
            return False
        self._blocks[position] = BLOCKS[block_id]
        return True

    def remove_block(self, position: Coordinate) -> Optional[Block]:
        """Remove the block at ``position`` and return it."""

        if not self.bounds.contains(position):
            return None
        return self._blocks.pop(position, None)

    def top_view(self, center: Coordinate, radius: int = 6) -> str:
        """Return an ASCII map centered around ``center``."""

        cx, _, cz = center
        lines = []
        for dz in range(radius, -radius - 1, -1):
            row = []
            for dx in range(-radius, radius + 1):
                x = cx + dx
                z = cz + dz
                if not (0 <= x < self.bounds.width and 0 <= z < self.bounds.depth):
                    row.append(" ")
                    continue
                top_block = self._top_block_symbol(x, z)
                row.append(top_block)
            lines.append("".join(row))
        return "\n".join(lines)

    def _top_block_symbol(self, x: int, z: int) -> str:
        symbols = {
            "grass": "▒",
            "sand": ".",
            "dirt": "░",
            "stone": "■",
            "water": "~",
            "log": "|",
            "leaves": "*",
            "planks": "#",
        }
        for y in range(self.bounds.height - 1, -1, -1):
            block = self._blocks.get((x, y, z))
            if block and block.id != "air":
                return symbols.get(block.id, "?")
        return " "

    def neighbors(self, position: Coordinate) -> Iterator[Coordinate]:
        x, y, z = position
        deltas = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        for dx, dy, dz in deltas:
            neighbor = (x + dx, y + dy, z + dz)
            if self.bounds.contains(neighbor):
                yield neighbor

    def describe(self, position: Coordinate) -> str:
        block = self.get_block(position)
        return f"{block.name}: {block.description}"

    def blocks(self) -> Iterable[Tuple[Coordinate, Block]]:
        return self._blocks.items()
