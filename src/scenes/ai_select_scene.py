"""Scene for selecting two AIs to battle in simulation mode."""

import pygame
from .scene import Scene
from src.config import *
from src.systems.ai_strategies import ALL_STRATEGIES


class AISelectScene(Scene):
    """Let the user pick two AIs from the four available strategies."""

    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.desc_font = pygame.font.Font(None, 26)

        self.strategies = ALL_STRATEGIES
        self.selected = [None, None]  # indices into self.strategies
        self.picking_slot = 0  # 0 = picking AI 1, 1 = picking AI 2

        # Build button rects
        self.ai_buttons = []
        btn_w, btn_h = 500, 70
        start_y = 200
        for i in range(len(self.strategies)):
            x = SCREEN_WIDTH // 2 - btn_w // 2
            y = start_y + i * (btn_h + 20)
            self.ai_buttons.append(pygame.Rect(x, y, btn_w, btn_h))

        self.start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100,
                                        start_y + len(self.strategies) * (btn_h + 20) + 20,
                                        200, 60)

    def update(self, delta_time: float) -> None:
        pass

    def render(self) -> None:
        self.screen.fill(BLACK)

        # Title
        if self.picking_slot == 0:
            title = self.font.render("Choose AI 1", True, WHITE)
        elif self.picking_slot == 1:
            title = self.font.render("Choose AI 2", True, WHITE)
        else:
            title = self.font.render("Ready to Simulate", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # Show current selections
        if self.selected[0] is not None:
            sel1 = self.small_font.render(
                f"AI 1: {self.strategies[self.selected[0]].name}", True, (100, 200, 255))
            self.screen.blit(sel1, (40, 130))
        if self.selected[1] is not None:
            sel2 = self.small_font.render(
                f"AI 2: {self.strategies[self.selected[1]].name}", True, (255, 150, 100))
            self.screen.blit(sel2, (40, 160))

        # AI buttons
        for i, (strat, rect) in enumerate(zip(self.strategies, self.ai_buttons)):
            # Highlight if selected
            if i == self.selected[0]:
                color = (40, 80, 160)
            elif i == self.selected[1]:
                color = (160, 60, 40)
            else:
                color = DARK_GRAY
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 2)

            name_text = self.small_font.render(strat.name, True, WHITE)
            name_rect = name_text.get_rect(midleft=(rect.x + 15, rect.y + 22))
            self.screen.blit(name_text, name_rect)

            desc_text = self.desc_font.render(strat.description, True, GRAY)
            desc_rect = desc_text.get_rect(midleft=(rect.x + 15, rect.y + 50))
            self.screen.blit(desc_text, desc_rect)

        # Start button (only when both selected)
        if self.selected[0] is not None and self.selected[1] is not None:
            pygame.draw.rect(self.screen, GREEN, self.start_button)
            start_text = self.small_font.render("Simulate 40", True, BLACK)
            start_rect = start_text.get_rect(center=self.start_button.center)
            self.screen.blit(start_text, start_rect)

        # Back hint
        back_text = self.desc_font.render("Press ESC to return to menu", True, GRAY)
        self.screen.blit(back_text, (20, SCREEN_HEIGHT - 40))

    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.next_scene = 'menu'
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Check AI buttons
            for i, rect in enumerate(self.ai_buttons):
                if rect.collidepoint(pos):
                    if self.picking_slot == 0:
                        self.selected[0] = i
                        self.picking_slot = 1
                    elif self.picking_slot == 1:
                        self.selected[1] = i
                        self.picking_slot = 2
                    break

            # Check start button
            if (self.selected[0] is not None and self.selected[1] is not None
                    and self.start_button.collidepoint(pos)):
                ai1 = self.strategies[self.selected[0]]
                ai2 = self.strategies[self.selected[1]]
                self.next_scene = ('ai_results', ai1, ai2)
