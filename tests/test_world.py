from minecraft.world import World


def test_world_generation_repeatable():
    world_a = World(width=16, depth=16, height=24, seed=1234)
    world_b = World(width=16, depth=16, height=24, seed=1234)
    assert dict(world_a.blocks()) == dict(world_b.blocks())


def test_column_height_non_zero():
    world = World(width=8, depth=8, height=16, seed=99)
    for x in range(world.bounds.width):
        for z in range(world.bounds.depth):
            assert world.column_height(x, z) >= 0


def test_spawn_position_on_surface():
    world = World(width=10, depth=10, height=20, seed=42)
    x, y, z = world.spawn_position()
    assert y == world.column_height(x, z)


def test_water_fills_below_sea_level():
    world = World(width=8, depth=8, height=20, seed=7)
    found_water = False
    for x in range(world.bounds.width):
        for z in range(world.bounds.depth):
            column_height = world.column_height(x, z)
            if column_height < world.sea_level:
                found_water = True
                for y in range(column_height + 1, min(world.sea_level + 1, world.bounds.height)):
                    assert world.get_block((x, y, z)).id == "water"
                break
        if found_water:
            break
    assert found_water, "Expected at least one body of water in the world"
