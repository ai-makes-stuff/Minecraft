"""A tiny text-based Minecraft-inspired sandbox."""

from .blocks import Block, BLOCKS, get_block
from .world import World
from .player import Player
from .game import Game

__all__ = ["Block", "BLOCKS", "get_block", "World", "Player", "Game"]
