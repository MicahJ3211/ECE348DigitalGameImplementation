"""Scene that runs the AI simulation and displays scrollable results."""

import pygame
from .scene import Scene
from src.config import *
from src.systems.ai_simulator import run_batch


class AIResultsScene(Scene):
    """Runs 40 AI vs AI games and shows scrollable results with deck buttons."""

    def __init__(self, screen: pygame.Surface, ai1=None, ai2=None):
        super().__init__(screen)
        self.font = pygame.font.Font(None, 44)
        self.small_font = pygame.font.Font(None, 30)
        self.row_font = pygame.font.Font(None, 26)
        self.detail_font = pygame.font.Font(None, 24)

        self.ai1 = ai1
        self.ai2 = ai2
        self.batch_result = None
        self.simulated = False

        # Scroll state
        self.scroll_y = 0
        self.row_height = 36
        self.header_height = 160  # space for summary at top

        # Deck view state
        self.viewing_deck = None  # (game_index, player: 1 or 2)
        self.deck_scroll_y = 0

        # Buttons
        self.menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT - 60, 200, 45)
        self.again_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 60, 200, 45)
        self.back_button = pygame.Rect(20, 20, 100, 40)

        # Clickable deck button rects (rebuilt each frame)
        self.deck_buttons = []

    def update(self, delta_time: float) -> None:
        if not self.simulated and self.ai1 and self.ai2:
            self.batch_result = run_batch(self.ai1, self.ai2, num_games=40)
            self.simulated = True

    def render(self) -> None:
        self.screen.fill(BLACK)

        if not self.simulated:
            loading = self.font.render("Simulating 40 games...", True, WHITE)
            self.screen.blit(loading, loading.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            return

        if self.viewing_deck is not None:
            self._render_deck_view()
            return

        self._render_results_list()

    def _render_results_list(self) -> None:
        """Render the scrollable game results list."""
        b = self.batch_result
        self.deck_buttons = []

        # --- Summary header (fixed, not scrolled) ---
        y = 15
        title = self.font.render("Simulation Results", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, y + 15)))
        y += 45

        matchup = self.small_font.render(f"{b.ai1_name}  vs  {b.ai2_name}", True, GRAY)
        self.screen.blit(matchup, matchup.get_rect(center=(SCREEN_WIDTH // 2, y)))
        y += 30

        ai1_pct = b.ai1_wins / max(1, b.total)
        ai2_pct = b.ai2_wins / max(1, b.total)

        # Win bar
        bar_w = 500
        bar_h = 24
        bar_x = SCREEN_WIDTH // 2 - bar_w // 2
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, y, bar_w, bar_h))
        w1 = int(bar_w * ai1_pct)
        wt = int(bar_w * (b.ties / max(1, b.total)))
        if w1 > 0:
            pygame.draw.rect(self.screen, (40, 100, 220), (bar_x, y, w1, bar_h))
        if wt > 0:
            pygame.draw.rect(self.screen, GRAY, (bar_x + w1, y, wt, bar_h))
        w2 = bar_w - w1 - wt
        if w2 > 0:
            pygame.draw.rect(self.screen, (200, 60, 40), (bar_x + w1 + wt, y, w2, bar_h))
        pygame.draw.rect(self.screen, WHITE, (bar_x, y, bar_w, bar_h), 1)
        y += bar_h + 8

        stats = self.detail_font.render(
            f"{b.ai1_name}: {b.ai1_wins}W ({ai1_pct*100:.0f}%)   "
            f"Ties: {b.ties}   "
            f"{b.ai2_name}: {b.ai2_wins}W ({ai2_pct*100:.0f}%)   "
            f"Avg rounds: {b.avg_rounds:.1f}",
            True, GRAY)
        self.screen.blit(stats, stats.get_rect(center=(SCREEN_WIDTH // 2, y + 8)))
        y += 28

        # --- Column headers ---
        header_y = y
        col_x = [30, 80, 260, 380, 440, 510, 580, 680, 780]
        headers = ["#", "Winner", "Reason", "Rnds", "P1 HP", "P2 HP", "P1 Vault", "P2 Vault", ""]
        # Extra columns for deck buttons handled below
        for i, h in enumerate(headers):
            txt = self.detail_font.render(h, True, WHITE)
            self.screen.blit(txt, (col_x[i] if i < len(col_x) else 0, header_y))
        # Deck button column headers
        self.detail_font.render("P1 Deck", True, WHITE)
        p1d_hdr = self.detail_font.render("P1 Deck", True, WHITE)
        p2d_hdr = self.detail_font.render("P2 Deck", True, WHITE)
        self.screen.blit(p1d_hdr, (880, header_y))
        self.screen.blit(p2d_hdr, (1000, header_y))

        # Divider
        pygame.draw.line(self.screen, GRAY, (20, header_y + 20), (SCREEN_WIDTH - 20, header_y + 20))
        list_top = header_y + 24

        # --- Scrollable rows ---
        visible_height = SCREEN_HEIGHT - list_top - 70  # leave room for buttons
        max_scroll = max(0, len(b.games) * self.row_height - visible_height)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))

        # Clip region
        clip_rect = pygame.Rect(0, list_top, SCREEN_WIDTH, visible_height)
        self.screen.set_clip(clip_rect)

        for i, g in enumerate(b.games):
            row_y = list_top + i * self.row_height - self.scroll_y
            if row_y + self.row_height < list_top or row_y > list_top + visible_height:
                continue

            if g.winner_id == 1:
                winner_name = b.ai1_name[:18]
                color = (100, 180, 255)
            elif g.winner_id == 2:
                winner_name = b.ai2_name[:18]
                color = (255, 130, 100)
            else:
                winner_name = "Tie"
                color = GRAY

            # Alternate row background
            if i % 2 == 0:
                pygame.draw.rect(self.screen, (25, 25, 35), (20, row_y, SCREEN_WIDTH - 40, self.row_height))

            vals = [f"{i+1}", winner_name, g.reason, str(g.rounds),
                    str(g.p1_health), str(g.p2_health), str(g.p1_vault), str(g.p2_vault)]
            for ci, v in enumerate(vals):
                txt = self.row_font.render(v, True, color)
                self.screen.blit(txt, (col_x[ci], row_y + 6))

            # Deck buttons
            p1_btn = pygame.Rect(880, row_y + 4, 90, self.row_height - 8)
            p2_btn = pygame.Rect(1000, row_y + 4, 90, self.row_height - 8)
            pygame.draw.rect(self.screen, (40, 80, 120), p1_btn)
            pygame.draw.rect(self.screen, WHITE, p1_btn, 1)
            pygame.draw.rect(self.screen, (120, 50, 40), p2_btn)
            pygame.draw.rect(self.screen, WHITE, p2_btn, 1)
            d1_txt = self.detail_font.render("View", True, WHITE)
            d2_txt = self.detail_font.render("View", True, WHITE)
            self.screen.blit(d1_txt, d1_txt.get_rect(center=p1_btn.center))
            self.screen.blit(d2_txt, d2_txt.get_rect(center=p2_btn.center))
            self.deck_buttons.append((p1_btn, i, 1))
            self.deck_buttons.append((p2_btn, i, 2))

        self.screen.set_clip(None)

        # --- Bottom buttons ---
        pygame.draw.rect(self.screen, BLUE, self.menu_button)
        self.screen.blit(self.small_font.render("Menu", True, WHITE),
                         self.small_font.render("Menu", True, WHITE).get_rect(center=self.menu_button.center))

        pygame.draw.rect(self.screen, GREEN, self.again_button)
        self.screen.blit(self.small_font.render("Run Again", True, BLACK),
                         self.small_font.render("Run Again", True, BLACK).get_rect(center=self.again_button.center))


    def _render_deck_view(self) -> None:
        """Render the 26-card deck list for a specific game/player."""
        game_idx, player_num = self.viewing_deck
        g = self.batch_result.games[game_idx]
        deck_cards = g.p1_deck if player_num == 1 else g.p2_deck
        ai_name = self.batch_result.ai1_name if player_num == 1 else self.batch_result.ai2_name
        player_color = (100, 180, 255) if player_num == 1 else (255, 130, 100)

        # Back button
        pygame.draw.rect(self.screen, DARK_GRAY, self.back_button)
        pygame.draw.rect(self.screen, WHITE, self.back_button, 1)
        back_txt = self.detail_font.render("Back", True, WHITE)
        self.screen.blit(back_txt, back_txt.get_rect(center=self.back_button.center))

        # Title
        title = self.font.render(f"Game {game_idx + 1} - {ai_name} Deck", True, player_color)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 50)))

        subtitle = self.small_font.render(f"26 cards selected during deck building", True, GRAY)
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 85)))

        # Sort cards by suit then rank for readability
        suit_order = {'Club': 0, 'Spade': 1, 'Heart': 2, 'Diamond': 3}
        rank_order = {r: i for i, r in enumerate(['A','2','3','4','5','6','7','8','9','10','J','Q','K'])}
        sorted_cards = sorted(deck_cards, key=lambda c: (suit_order.get(c.suit, 9), rank_order.get(c.rank, 99)))

        # Render as a grid of card rectangles
        card_w, card_h = 80, 110
        spacing = 12
        cards_per_row = 9
        start_x = (SCREEN_WIDTH - cards_per_row * (card_w + spacing) + spacing) // 2
        start_y = 120

        suit_colors = {
            'Club': (0, 128, 0),
            'Spade': (30, 30, 30),
            'Heart': (200, 40, 40),
            'Diamond': (200, 120, 0),
        }

        for idx, card in enumerate(sorted_cards):
            row = idx // cards_per_row
            col = idx % cards_per_row
            x = start_x + col * (card_w + spacing)
            y = start_y + row * (card_h + spacing) - self.deck_scroll_y

            if y + card_h < 100 or y > SCREEN_HEIGHT - 70:
                continue

            bg_color = suit_colors.get(card.suit, DARK_GRAY)
            rect = pygame.Rect(x, y, card_w, card_h)
            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 2)

            # Rank
            rank_txt = self.small_font.render(card.rank, True, WHITE)
            self.screen.blit(rank_txt, rank_txt.get_rect(center=(x + card_w // 2, y + 30)))

            # Suit
            suit_txt = self.detail_font.render(card.suit, True, WHITE)
            self.screen.blit(suit_txt, suit_txt.get_rect(center=(x + card_w // 2, y + 60)))

            # Base damage
            dmg_txt = self.detail_font.render(f"Dmg: {card.get_base_damage()}", True, (200, 200, 200))
            self.screen.blit(dmg_txt, dmg_txt.get_rect(center=(x + card_w // 2, y + 88)))

        # Suit summary at bottom
        summary_y = SCREEN_HEIGHT - 55
        counts = {}
        for c in sorted_cards:
            counts[c.suit] = counts.get(c.suit, 0) + 1
        face_count = sum(1 for c in sorted_cards if c.is_face_card())
        summary = f"Clubs: {counts.get('Club',0)}  Spades: {counts.get('Spade',0)}  Hearts: {counts.get('Heart',0)}  Diamonds: {counts.get('Diamond',0)}  Face cards: {face_count}"
        sum_txt = self.detail_font.render(summary, True, GRAY)
        self.screen.blit(sum_txt, sum_txt.get_rect(center=(SCREEN_WIDTH // 2, summary_y)))

    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.viewing_deck is not None:
                self.viewing_deck = None
                self.deck_scroll_y = 0
            else:
                self.next_scene = 'menu'
            return

        if event.type == pygame.MOUSEWHEEL:
            if self.viewing_deck is not None:
                self.deck_scroll_y -= event.y * 30
                self.deck_scroll_y = max(0, self.deck_scroll_y)
            else:
                self.scroll_y -= event.y * self.row_height
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.viewing_deck is not None:
                # Back button in deck view
                if self.back_button.collidepoint(pos):
                    self.viewing_deck = None
                    self.deck_scroll_y = 0
                return

            # Check deck buttons
            for btn_rect, game_idx, player_num in self.deck_buttons:
                if btn_rect.collidepoint(pos):
                    self.viewing_deck = (game_idx, player_num)
                    self.deck_scroll_y = 0
                    return

            # Bottom buttons
            if self.menu_button.collidepoint(pos):
                self.next_scene = 'menu'
            elif self.again_button.collidepoint(pos) and self.simulated:
                self.simulated = False
                self.scroll_y = 0
