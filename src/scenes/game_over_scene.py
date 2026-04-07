import pygame
from .scene import Scene
from src.config import *


class GameOverScene(Scene):
    """Game over scene."""
    
    def __init__(self, screen: pygame.Surface, win_condition=None):
        super().__init__(screen)
        self.win_condition = win_condition
        self.font = pygame.font.Font(None, 74)
        self.button_font = pygame.font.Font(None, 48)
        
        # Menu button
        self.menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60)
    
    def update(self, delta_time: float) -> None:
        pass
    
    def render(self) -> None:
        self.screen.fill(BLACK)
        
        # Game Over text
        title = self.font.render("Game Over", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)
        
        # Winner text
        if self.win_condition:
            if self.win_condition.winner_id == 1:
                winner_text = self.font.render("You Win!", True, GREEN)
            elif self.win_condition.winner_id == 2:
                winner_text = self.font.render("AI Wins!", True, RED)
            else:
                winner_text = self.font.render("Tie!", True, GRAY)
            
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(winner_text, winner_rect)
        
        # Menu button
        pygame.draw.rect(self.screen, BLUE, self.menu_button)
        menu_text = self.button_font.render("Menu", True, WHITE)
        menu_rect = menu_text.get_rect(center=self.menu_button.center)
        self.screen.blit(menu_text, menu_rect)
    
    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.menu_button.collidepoint(event.pos):
                self.next_scene = 'menu'
