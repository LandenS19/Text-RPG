# Text-RPG

Text-RPG is a simple, extensible text-based role-playing game written in Python. Players pick a class, manage resources (health, mana, items), and engage in turn-based encounters with enemies. The project is designed for learning, prototyping game mechanics, and extending with new classes, abilities, and content.

## Features
- Turn-based combat system (player vs. enemy)
- Multiple playable classes with distinct stats and abilities
- Simple inventory and consumable support
- Easy-to-extend codebase for adding enemies, items, and mechanics

## Player classes
Class definitions and base stats live in the file `Character Clases` (CLASSES_STATS). The project contains a set of archetypes (Warrior, Mage, Rogue, Paladin, etc.) each with a stats dictionary you can adjust or extend.

## Running the game
Run the main script (replace with the actual entry point if different):
python main.py

If the project uses a different entry file, run that file instead.

## Project layout (typical)
- Character Clases — class stats and definitions (CLASSES_STATS)
- main.py — game entry point (may be named differently)
- README.md — this file
- tests/ — unit tests (if present)
- assets/ — text or data files (if present)

## Extending the project
- Implement new abilities and items in the combat or player modules.
