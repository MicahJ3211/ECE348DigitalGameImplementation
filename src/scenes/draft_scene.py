"""Card drafting scene — alternating picks from a shared 52-card pool."""

import random
import pygame
from .scene import Scene
from src.entities.card import Card
from src.config import *


class DraftScene(Scene):
    """Players take turns drafting cards from a shared pool of 52."""

    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.font = pygame.font.Font(None, 44)
        self.small_font = pygame.font.Font(None, 30)
        self.detail_font = pygame.font.Font(None, 24)
        self.card_font = pygame.font.Font(None, 22)

        # Build full 52-card pool
        self.pool = [Card(rank=r, suit=s) for s in SUITS for r in RANKS]

        # Sort for display: by suit then rank
        suit_order = {'Club': 0, 'Spade': 1, 'Heart': 2, 'Diamond': 3}
        rank_order = {r: i for i, r in enumerate(RANKS)}
        self.pool.sort(key=lambda c: (suit_order[c.suit], rank_order[c.rank]))

        # Track which cards are taken
        self.taken = {}  # index -> 'player' or 'ai'
        self.player_cards = []
        self.ai_cards = []

        # Turn state: 50% chance who goes first
        self.player_turn = random.choice([True, False])
        self.ai_think_timer = 0.0  # small delay so AI pick is visible
        self.draft_complete = False

        # Card grid layout
        self.card_w = 72
        self.card_h = 100
        self.spacing = 8
        self.cards_per_row = 13
        self.grid_x = (SCREEN_WIDTH - self.cards_per_row * (self.card_w + self.spacing) + self.spacing) // 2
        self.grid_y = 120

        # Hover state
        self.mouse_pos = (0, 0)
        self.hovered_index = -1

        # Suit colors
        self.suit_colors = {
            'Club': (0, 128, 0),
            'Spade': (40, 40, 40),
            'Heart': (200, 40, 40),
            'Diamond': (200, 120, 0),
        }

    def update(self, delta_time: float) -> None:
        if self.draft_complete:
            return

        # Check if draft is done
        if len(self.player_cards) == 26 and len(self.ai_cards) == 26:
            self.draft_complete = True
            return

        # AI turn with a small delay
        if not self.player_turn:
            self.ai_think_timer += delta_time
            if self.ai_think_timer >= 0.3:
                self._ai_pick()
                self.ai_think_timer = 0.0
                self.player_turn = True


    def _ai_pick(self) -> None:
        """AI picks the highest-value available card."""
        available = [(i, c) for i, c in enumerate(self.pool) if i not in self.taken]
        if not available:
            return
        # Score: face cards high, then by base damage, slight suit preference
        def score(pair):
            _, c = pair
            return c.get_base_damage()
        available.sort(key=score, reverse=True)
        # Pick from top 5 randomly for some variety
        top = available[:min(5, len(available))]
        idx, card = random.choice(top)
        self.taken[idx] = 'ai'
        self.ai_cards.append(card)

    def _get_card_rect(self, index: int) -> pygame.Rect:
        """Get the screen rect for a card at the given pool index."""
        row = index // self.cards_per_row
        col = index % self.cards_per_row
        x = self.grid_x + col * (self.card_w + self.spacing)
        y = self.grid_y + row * (self.card_h + self.spacing)
        return pygame.Rect(x, y, self.card_w, self.card_h)

    def render(self) -> None:
        self.screen.fill(BLACK)

        # Title / turn indicator
        if self.draft_complete:
            title = self.font.render("Draft Complete! Press SPACE to play", True, GREEN)
        elif self.player_turn:
            title = self.font.render("Your Pick", True, (100, 200, 255))
        else:
            title = self.font.render("AI is picking...", True, (255, 150, 100))
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 30)))

        # Counts
        count_txt = self.small_font.render(
            f"You: {len(self.player_cards)}/26    AI: {len(self.ai_cards)}/26",
            True, GRAY)
        self.screen.blit(count_txt, count_txt.get_rect(center=(SCREEN_WIDTH // 2, 65)))

        # Who went first
        first_txt = self.detail_font.render(
            f"{'You' if len(self.player_cards) + len(self.ai_cards) > 0 and self.player_cards and self.taken.get(min(self.taken.keys(), default=-1)) == 'player' else 'AI'} picked first",
            True, DARK_GRAY)
        self.screen.blit(first_txt, (20, SCREEN_HEIGHT - 25))

        # Card grid
        self.hovered_index = -1
        for i, card in enumerate(self.pool):
            rect = self._get_card_rect(i)

            if i in self.taken:
                # Taken card — show dimmed with owner color
                owner = self.taken[i]
                if owner == 'player':
                    bg = (20, 40, 80)
                    border = (60, 120, 200)
                    label = "YOU"
                else:
                    bg = (80, 25, 20)
                    border = (200, 80, 60)
                    label = "AI"
                pygame.draw.rect(self.screen, bg, rect)
                pygame.draw.rect(self.screen, border, rect, 2)
                lbl = self.detail_font.render(label, True, border)
                self.screen.blit(lbl, lbl.get_rect(center=rect.center))
            else:
                # Available card
                bg = self.suit_colors.get(card.suit, DARK_GRAY)
                pygame.draw.rect(self.screen, bg, rect)

                # Hover highlight
                if rect.collidepoint(self.mouse_pos) and self.player_turn and not self.draft_complete:
                    pygame.draw.rect(self.screen, (255, 255, 100), rect, 3)
                    self.hovered_index = i
                else:
                    pygame.draw.rect(self.screen, WHITE, rect, 1)

                # Rank
                rank_txt = self.small_font.render(card.rank, True, WHITE)
                self.screen.blit(rank_txt, rank_txt.get_rect(center=(rect.centerx, rect.y + 25)))

                # Suit initial
                suit_txt = self.card_font.render(card.suit, True, WHITE)
                self.screen.blit(suit_txt, suit_txt.get_rect(center=(rect.centerx, rect.y + 50)))

                # Base damage
                dmg_txt = self.card_font.render(str(card.get_base_damage()), True, (180, 180, 180))
                self.screen.blit(dmg_txt, dmg_txt.get_rect(center=(rect.centerx, rect.y + 75)))

        # Player's drafted cards summary (bottom bar)
        self._render_draft_summary()

    def _render_draft_summary(self) -> None:
        """Render a compact summary of the player's drafted cards at the bottom."""
        y = SCREEN_HEIGHT - 60
        pygame.draw.rect(self.screen, (15, 15, 25), (0, y - 5, SCREEN_WIDTH, 65))

        if not self.player_cards:
            hint = self.detail_font.render("Click a card to draft it", True, GRAY)
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, y + 20)))
            return

        # Show mini cards
        mini_w = 28
        mini_spacing = 3
        total_w = len(self.player_cards) * (mini_w + mini_spacing)
        start_x = max(10, (SCREEN_WIDTH - total_w) // 2)

        for i, card in enumerate(self.player_cards):
            x = start_x + i * (mini_w + mini_spacing)
            color = self.suit_colors.get(card.suit, DARK_GRAY)
            r = pygame.Rect(x, y, mini_w, 40)
            pygame.draw.rect(self.screen, color, r)
            pygame.draw.rect(self.screen, WHITE, r, 1)
            txt = self.card_font.render(card.rank, True, WHITE)
            self.screen.blit(txt, txt.get_rect(center=r.center))

    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.next_scene = 'menu'
            return

        if self.draft_complete:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Transition to gameplay with drafted cards
                self.next_scene = ('gameplay_draft', self.player_cards, self.ai_cards)
            return

        # Player picks a card
        if self.player_turn and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered_index >= 0 and self.hovered_index not in self.taken:
                self.taken[self.hovered_index] = 'player'
                self.player_cards.append(self.pool[self.hovered_index])
                self.player_turn = False
                self.ai_think_timer = 0.0
