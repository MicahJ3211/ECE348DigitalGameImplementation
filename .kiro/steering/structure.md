# Project Structure

## Organization

Pygame projects follow a modular structure separating game logic, rendering, assets, and configuration.

## Directory Layout

```
.kiro/
  steering/     # AI assistant guidance documents
  specs/        # Feature specifications and implementation plans

src/
  main.py       # Entry point and game loop
  game.py       # Core game class and state manager
  scenes/       # Game scenes/states (menu, deck builder, gameplay, game over)
  entities/     # Game entities (card, player, vault, deck)
  components/   # Reusable components (animation, ui_elements)
  systems/      # Game systems (combat, ability_resolver, input, audio)
  utils/        # Helper functions and utilities
  config.py     # Game configuration and constants (starting health, vault rules)

assets/
  images/       # Sprites, backgrounds, UI elements
  sounds/       # Sound effects
  music/        # Background music
  fonts/        # Custom fonts
  data/         # Level data, JSON configs

tests/
  test_entities/
  test_systems/
  test_utils/

requirements.txt  # Python dependencies
README.md        # Project documentation
```

## Conventions

- Use snake_case for Python files and directories
- Group related functionality by feature (entities, systems, scenes)
- Keep game loop in main.py, delegate logic to game.py
- Use scene/state pattern for different game screens
- Separate entity logic from rendering
- Store all magic numbers in config.py
- Keep assets organized by type

## File Naming

- Python modules: snake_case (player.py, enemy_manager.py)
- Classes: PascalCase (Player, EnemyManager)
- Functions/variables: snake_case (update_position, player_speed)
- Constants: UPPER_SNAKE_CASE (SCREEN_WIDTH, MAX_ENEMIES)
- Asset files: lowercase with hyphens (player-sprite.png, jump-sound.wav)
