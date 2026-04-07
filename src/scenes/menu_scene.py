import pygame
from .scene import Scene
from src.config import *


class MenuScene(Scene):
    """Main menu scene."""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.font = pygame.font.Font(None, 74)
        self.button_font = pygame.font.Font(None, 48)
        
        # Buttons
        cx = SCREEN_WIDTH // 2
        self.start_button = pygame.Rect(cx - 120, SCREEN_HEIGHT // 2 - 50, 240, 60)
        self.ai_battle_button = pygame.Rect(cx - 120, SCREEN_HEIGHT // 2 + 30, 240, 60)
        
    def update(self, delta_time: float) -> None:
        pass
    
    def render(self) -> None:
        self.screen.fill(BLACK)
        
        # Title
        title = self.font.render("Card Game", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)
        
        # Start button
        pygame.draw.rect(self.screen, GREEN, self.start_button)
        start_text = self.button_font.render("Play", True, BLACK)
        self.screen.blit(start_text, start_text.get_rect(center=self.start_button.center))
        
        # AI Battle button
        pygame.draw.rect(self.screen, (60, 60, 180), self.ai_battle_button)
        ai_text = self.button_font.render("AI Battle", True, WHITE)
        self.screen.blit(ai_text, ai_text.get_rect(center=self.ai_battle_button.center))
    
    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.collidepoint(event.pos):
                self.next_scene = 'gameplay'
            elif self.ai_battle_button.collidepoint(event.pos):
                self.next_scene = 'ai_select'
