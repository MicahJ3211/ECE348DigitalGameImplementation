import pygame
from typing import Dict, Optional, Any
from src.scenes.scene import Scene
from src.scenes.menu_scene import MenuScene
from src.scenes.deck_builder_scene import DeckBuilderScene
from src.scenes.gameplay_scene import GameplayScene
from src.scenes.game_over_scene import GameOverScene


class SceneManager:
    """Manages scene transitions and lifecycle."""
    
    def __init__(self, game_engine):
        """
        Initialize scene manager with game engine reference.
        
        Args:
            game_engine: Reference to the main GameEngine
        """
        self.game_engine = game_engine
        self.scenes: Dict[str, type] = {}
        self.current_scene: Optional[Scene] = None
        self.scene_data: Dict[str, Any] = {}
        
        # Register all scene types
        self._register_scenes()
        
        # Start with menu scene
        self.change_scene('menu')
    
    def _register_scenes(self) -> None:
        """Register all available scene types."""
        self.scenes['menu'] = MenuScene
        self.scenes['deck_builder'] = DeckBuilderScene
        self.scenes['gameplay'] = GameplayScene
        self.scenes['game_over'] = GameOverScene
    
    def change_scene(self, scene_name: str, **kwargs) -> None:
        """
        Transition to a new scene.
        
        Args:
            scene_name: Name of the scene to transition to
            **kwargs: Additional data to pass to the new scene
        """
        if scene_name not in self.scenes:
            raise ValueError(f"Unknown scene: {scene_name}")
        
        # Store any data passed for the scene
        self.scene_data = kwargs
        
        # Create new scene instance
        scene_class = self.scenes[scene_name]
        self.current_scene = scene_class(self.game_engine)
        
        # Pass any additional data to the scene
        for key, value in kwargs.items():
            if hasattr(self.current_scene, key):
                setattr(self.current_scene, key, value)
    
    def update(self, delta_time: float) -> None:
        """
        Update the current scene.
        
        Args:
            delta_time: Time since last frame in seconds
        """
        if self.current_scene:
            self.current_scene.update(delta_time)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the current scene.
        
        Args:
            screen: The pygame surface to render to
        """
        if self.current_scene:
            self.current_scene.render(screen)
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """
        Handle input for the current scene.
        
        Args:
            event: The pygame event to handle
        """
        if self.current_scene:
            self.current_scene.handle_input(event)
    
    def get_current_scene(self) -> Optional[Scene]:
        """
        Get the current active scene.
        
        Returns:
            The current Scene instance or None
        """
        return self.current_scene
