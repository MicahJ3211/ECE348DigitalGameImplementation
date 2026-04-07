# Product Overview

A strategic two-player card game built with Python and pygame, featuring simultaneous card play, resource management, and complex card interactions.

## Purpose

Create a competitive card game where players build custom decks and engage in tactical battles using a unique combat system with health, defense, vault mechanics, and special card abilities.

## Game Summary

Players compete in rounds by simultaneously playing 3 cards from their hand. Cards deal damage based on rank and suit/face abilities. Winners collect cards to their vault, which powers future abilities. Victory comes from reducing opponent's health to 0 or having the largest vault when cards run out.

See `game-rules.md` for complete rules and mechanics.

## Key Features

### Game Mechanics
- Deck construction (26 cards per player)
- Simultaneous card play (3 cards per round)
- Vault system for won cards
- Health, defense, and damage tracking
- Four suit abilities (Club, Spade, Heart, Diamond)
- Four face card abilities (Ace, Jack, Queen, King)
- Card shedding mechanic for strategic resource trade-offs
- Complex order of operations for ability resolution

### Technical Features
- Game loop with consistent frame rate
- Mouse input for card selection and placement
- Card rendering and animations
- UI for health, defense, and vault display
- Scene management (menu, deck building, gameplay, game over)
- Turn-based state management
- Ability resolution system
- Audio system (sound effects and music)

## Design Principles

- Clear visual feedback for card abilities and combat resolution
- Intuitive card selection and placement interface
- Strategic depth through vault management and ability timing
- Transparent order of operations display
- Accessible tutorial for complex mechanics
- Smooth animations for combat flow

## Target Platform

Desktop (Windows, macOS, Linux) via Python interpreter
