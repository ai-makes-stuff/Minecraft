from minecraft.game import Game


def test_help_lists_commands():
    game = Game(width=8, depth=8, height=16, seed=5)
    text = game.execute("help")
    assert "look" in text
    assert "quit" in text


def test_move_command_reports_position():
    game = Game(width=8, depth=8, height=16, seed=6)
    response = game.execute("move north")
    assert "You move" in response or "cannot move" in response


def test_inventory_command_mentions_planks():
    game = Game(width=8, depth=8, height=16, seed=10)
    response = game.execute("inventory")
    assert "Planks" in response


def test_unknown_command():
    game = Game(width=8, depth=8, height=16, seed=7)
    response = game.execute("fly")
    assert "do not understand" in response
