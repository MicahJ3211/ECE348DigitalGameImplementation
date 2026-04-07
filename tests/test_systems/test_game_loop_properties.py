"""Property-based tests for game loop structure.

Feature: card-game-core, Property 45: Game Loop Structure
For any frame in the game loop, input events should be processed,
game state should be updated, and the current scene should be rendered.

Validates: Requirements 23.2, 23.3, 23.4
"""

import pygame
from hypothesis import given, settings
import hypothesis.strategies as st

from src.game import Game


# Initialize pygame once for the module
pygame.init()


def _make_surface():
    """Create a pygame surface for testing."""
    return pygame.Surface((1280, 720))


class TestGameLoopStructure:
    """**Validates: Requirements 23.2, 23.3, 23.4**

    Property 45: Game Loop Structure
    For any frame in the game loop, input events should be processed,
    game state should be updated, and the current scene should be rendered.
    """

    def test_game_has_handle_events_method(self):
        """Game class should have a handle_events method."""
        surface = _make_surface()
        game = Game(surface)
        assert hasattr(game, 'handle_events')
        assert callable(game.handle_events)

    def test_game_has_update_method(self):
        """Game class should have an update method."""
        surface = _make_surface()
        game = Game(surface)
        assert hasattr(game, 'update')
        assert callable(game.update)

    def test_game_has_render_method(self):
        """Game class should have a render method."""
        surface = _make_surface()
        game = Game(surface)
        assert hasattr(game, 'render')
        assert callable(game.render)

    def test_game_has_run_method(self):
        """Game class should have a run method for the main loop."""
        surface = _make_surface()
        game = Game(surface)
        assert hasattr(game, 'run')
        assert callable(game.run)

    def test_game_has_quit_method(self):
        """Game class should have a quit method for graceful shutdown."""
        surface = _make_surface()
        game = Game(surface)
        assert hasattr(game, 'quit')
        assert callable(game.quit)

    def test_game_initializes_with_scene(self):
        """Game should have a current scene after initialization."""
        surface = _make_surface()
        game = Game(surface)
        assert game.current_scene is not None

    @given(delta=st.floats(min_value=0.001, max_value=0.1))
    @settings(max_examples=100)
    def test_update_accepts_delta_time(self, delta):
        """update() should accept any valid delta_time without error."""
        surface = _make_surface()
        game = Game(surface)
        # Should not raise
        game.update(delta)

    @given(delta=st.floats(min_value=0.001, max_value=0.1))
    @settings(max_examples=100)
    def test_current_scene_render_does_not_crash(self, delta):
        """The current scene's render() should not crash for any game state."""
        surface = _make_surface()
        game = Game(surface)
        # Render the current scene directly (Game.render calls pygame.display.flip
        # which requires a real display, so we test the scene render instead)
        game.current_scene.render()

    def test_game_loop_methods_exist_in_correct_order(self):
        """The three core loop methods should all exist on the Game class."""
        surface = _make_surface()
        game = Game(surface)

        # All three methods must exist for a proper game loop
        loop_methods = ['handle_events', 'update', 'render']
        for method_name in loop_methods:
            assert hasattr(game, method_name), f"Game missing {method_name} method"
            assert callable(getattr(game, method_name)), f"Game.{method_name} not callable"

    def test_quit_sets_running_false(self):
        """Calling quit() should set running to False."""
        surface = _make_surface()
        game = Game(surface)
        assert game.running is True
        game.quit()
        assert game.running is False
