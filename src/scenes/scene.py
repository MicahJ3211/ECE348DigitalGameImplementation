from abc import ABC, abstractmethod
import pygame


class Scene(ABC):
    """Base class for all game scenes."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.next_scene = None
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update scene logic."""
        pass
    
    @abstractmethod
    def render(self) -> None:
        """Render scene to screen."""
        pass
    
    @abstractmethod
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        pass
