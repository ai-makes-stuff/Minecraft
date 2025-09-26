# Mini Minecraft Sandbox

This project is a small text-based sandbox that captures a slice of the Minecraft experience. It generates a miniature voxel world, lets you explore it with simple commands, and supports harvesting, placing, and crafting a handful of block types.

## Features

* Procedural overworld generation with grasslands, sandy beaches, water, and the occasional tree.
* A `Player` avatar who can walk across the landscape, climb, and inspect nearby blocks.
* Inventory management with harvesting and placing of blocks.
* Basic crafting: turn gathered logs into stacks of wooden planks.
* ASCII map rendering that shows the surrounding area from a top-down perspective.

## Getting Started

The project has no external dependencies beyond the Python standard library.

```bash
python main.py
```

Type `help` inside the game for a full list of commands. Example session:

```
Welcome to the miniature Minecraft sandbox! Type 'help' for instructions.
> look
You are standing above grass.
There is air at head height.
Beneath you lies dirt.

▒▒▒▒▒▒▒
▒▒▒▒▒▒▒
▒▒▒▒▒▒▒
▒▒▒▒▒▒▒
▒▒▒▒▒▒▒
▒▒▒▒▒▒▒
▒▒▒▒▒▒▒
> harvest up
You gather one Oak Leaves.
> craft planks
You do not have the resources to craft that.
> quit
Thanks for playing!
```

## Running Tests

```
pytest
```

The test suite checks the most important mechanics, such as terrain generation, inventory management, and crafting.
