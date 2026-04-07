# Technology Stack

## Build System

Python with pip for dependency management. Consider using virtual environments (venv) to isolate project dependencies.

## Tech Stack

- Language: Python 3.8+
- Game Library: pygame
- Runtime: Python interpreter

## Common Commands

### Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Development
```bash
# Run the game
python main.py

# Run tests
python -m pytest tests/

# Run with debug mode (if implemented)
python main.py --debug
```

### Code Quality
```bash
# Format code
black .

# Lint code
pylint src/

# Type checking
mypy src/
```

## Dependencies

Core dependencies:
- pygame: Game engine and rendering
- pytest: Testing framework (dev dependency)

Optional dependencies:
- black: Code formatting
- pylint: Linting
- mypy: Type checking

## Development Guidelines

- Follow PEP 8 style guide for Python code
- Use type hints for function signatures
- Keep game loop at 60 FPS target
- Separate game logic from rendering
- Use pygame's sprite groups for entity management
- Handle events in a centralized event loop
- Keep asset loading separate from game logic
- Use constants for magic numbers (screen size, colors, speeds)
- Profile performance-critical sections
- Test game logic independently from pygame rendering
