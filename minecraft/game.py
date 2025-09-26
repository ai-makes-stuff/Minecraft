"""Text adventure style interface for the sandbox."""
from __future__ import annotations

from typing import List, Optional

from .blocks import BLOCKS
from .player import Player
from .world import World


class Game:
    """High level façade exposing the sandbox via textual commands."""

    def __init__(
        self,
        *,
        width: int = 32,
        depth: int = 32,
        height: int = 32,
        seed: Optional[int] = None,
    ) -> None:
        self.world = World(width=width, depth=depth, height=height, seed=seed)
        self.player = Player(self.world)

    # ------------------------------------------------------------------
    # Command handling

    def execute(self, command: str) -> str:
        """Execute ``command`` and return the response string."""

        command = command.strip()
        if not command:
            return ""
        parts = command.split()
        action = parts[0].lower()
        args = parts[1:]

        if action in {"quit", "exit"}:
            return "Thanks for playing!"
        if action in {"help", "?"}:
            return self._help_text()
        if action in {"look", "see"}:
            return self._look()
        if action in {"map"}:
            return self._map(args)
        if action in {"move", "walk", "go"}:
            return self._move(args)
        if action in {"harvest", "mine", "break", "dig"}:
            return self._harvest(args)
        if action in {"place", "build"}:
            return self._place(args)
        if action in {"inventory", "inv"}:
            return self.player.inventory_summary()
        if action == "craft":
            return self._craft(args)
        if action in {"where", "pos"}:
            x, y, z = self.player.position
            return f"You are at ({x}, {y}, {z})."
        return f"I do not understand '{command}'. Type 'help' for options."

    def _help_text(self) -> str:
        return (
            "Commands:\n"
            "  look                - describe nearby blocks\n"
            "  map [radius]        - show a top-down map around you\n"
            "  move <dir>          - walk north, south, east or west\n"
            "  harvest [dir]       - break the block in a direction\n"
            "  place <block> [dir] - place a block if you have one\n"
            "  craft <block>       - craft items if you have the resources\n"
            "  inventory           - list carried blocks\n"
            "  where               - show your current position\n"
            "  quit                - exit the game"
        )

    def _look(self) -> str:
        description = self.player.describe_surroundings()
        map_view = self.world.top_view(self.player.position, radius=4)
        return f"{description}\n\n{map_view}"

    def _map(self, args: List[str]) -> str:
        radius = 6
        if args:
            try:
                radius = max(1, min(10, int(args[0])))
            except ValueError:
                return "Map radius must be a number."
        return self.world.top_view(self.player.position, radius=radius)

    def _move(self, args: List[str]) -> str:
        if not args:
            return "Move where? Try north, south, east or west."
        direction = args[0].lower()
        try:
            moved = self.player.move(direction)
        except ValueError as exc:  # Unknown direction
            return str(exc)
        if moved:
            x, y, z = self.player.position
            return f"You move {direction} to ({x}, {y}, {z})."
        return "You cannot move in that direction."

    def _harvest(self, args: List[str]) -> str:
        direction = args[0].lower() if args else None
        try:
            block_id = self.player.harvest(direction)
        except ValueError as exc:
            return str(exc)
        if block_id is None:
            return "There is nothing to harvest there."
        block_name = BLOCKS[block_id].name
        return f"You gather one {block_name}."

    def _place(self, args: List[str]) -> str:
        if not args:
            return "Place what?"
        block_id = args[0].lower()
        direction = args[1].lower() if len(args) > 1 else None
        if block_id not in BLOCKS:
            return f"Unknown block type '{block_id}'."
        try:
            placed = self.player.place(block_id, direction)
        except ValueError as exc:
            return str(exc)
        if placed:
            return f"You place a {BLOCKS[block_id].name}."
        return "You cannot place a block there."

    def _craft(self, args: List[str]) -> str:
        if not args:
            return "Craft what?"
        block_id = args[0].lower()
        if block_id not in BLOCKS:
            return f"Unknown block type '{block_id}'."
        crafted = self.player.craft(block_id)
        if crafted:
            return f"You craft {BLOCKS[block_id].name}."
        return "You do not have the resources to craft that."

    # ------------------------------------------------------------------
    # Interactive loop

    def run(self) -> None:  # pragma: no cover - the interactive loop is hard to test.
        print("Welcome to the miniature Minecraft sandbox! Type 'help' for instructions.")
        while True:
            try:
                command = input("> ")
            except EOFError:
                print()
                break
            response = self.execute(command)
            print(response)
            if command.strip().lower() in {"quit", "exit"}:
                break
