"""Entry point for the miniature Minecraft sandbox."""
from __future__ import annotations

from minecraft.game import Game


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
