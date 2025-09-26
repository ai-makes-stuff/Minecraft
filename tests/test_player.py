from minecraft.player import Player
from minecraft.world import World


def make_player(seed: int = 1) -> Player:
    world = World(width=12, depth=12, height=20, seed=seed)
    return Player(world)


def test_player_starts_with_planks():
    player = make_player()
    assert player.inventory["planks"] == 8


def test_player_move_horizontal_changes_column():
    player = make_player()
    original = player.position
    moved = player.move("north")
    assert moved
    assert player.position != original


def test_player_harvest_and_place_cycle():
    player = make_player()
    x, y, z = player.position
    target = (x, y + 1, z)
    player.world.set_block(target, "log")
    harvested = player.harvest()
    assert harvested == "log"
    assert player.inventory["log"] >= 1
    placed = player.place("log")
    assert placed
    assert player.world.get_block(target).id == "log"
    assert player.inventory.get("log", 0) == 0
