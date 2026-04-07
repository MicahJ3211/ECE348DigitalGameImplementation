import pygame
import random
from .scene import Scene
from src.config import *
from src.entities import Card, Player, Vault, Deck
from src.systems.combat_system import CombatSystem
from src.systems.ability_resolver import AbilityResolver
from src.systems.ui_manager import UIManager


class GameplayScene(Scene):
    """Enhanced gameplay scene with animations and clear UI."""
    
    def __init__(self, screen: pygame.Surface, player_cards=None, ai_cards=None):
        super().__init__(screen)
        
        # Initialize UI Manager
        self.ui_manager = UIManager(screen)
        
        # Initialize game (with optional drafted cards)
        self.setup_game(player_cards, ai_cards)
        
        # UI state
        self.selected_cards = []
        self.round_phase = 'selection'  # 'selection', 'reveal', 'show_effects', 'show_results'
        self.round_number = 1
        self.animation_timer = 0
        self.show_combat_summary = False
        
        # Effect queue: list of dicts describing each effect to show one at a time
        self.effect_queue = []
        self.current_effect_index = 0
        
        # Queen disable state
        self.queen_disable_count = 0       # how many opponent cards the player can disable
        self.queen_disabled_indices = []   # indices the player has clicked so far
        self.queen_card_rects = []         # click rects for opponent's face-down cards
        
        # Last round results for display
        self.last_p1_damage = 0
        self.last_p2_damage = 0
        self.last_winner_id = None
        
        # Hover tooltip state
        self.mouse_pos = (0, 0)
        self.hovered_card_index = -1
        
    def setup_game(self, player_cards=None, ai_cards=None):
        """Initialize players and deck. Uses drafted cards if provided."""
        if player_cards and ai_cards:
            # Use pre-drafted cards
            all_cards = list(player_cards) + list(ai_cards)
        else:
            # Fallback: create full deck (for quick-play without drafting)
            all_cards = []
            for suit in SUITS:
                for rank in RANKS:
                    all_cards.append(Card(rank=rank, suit=suit))
        
        # Create deck and shuffle
        deck = Deck(all_cards)
        deck.shuffle()
        
        # Create players
        self.player1 = Player(player_id=0, vault=Vault())  # Human player
        self.player2 = Player(player_id=1, vault=Vault())  # AI player
        
        # Deal initial hands
        self.player1.hand = deck.draw(STARTING_HAND_SIZE)
        self.player2.hand = deck.draw(STARTING_HAND_SIZE)
        
        # Assign deck to players
        self.player1.deck = deck
        self.player2.deck = deck
        
        # Combat system and ability resolver
        self.combat_system = CombatSystem()
        self.ability_resolver = AbilityResolver(self.combat_system)
        
        # Played cards
        self.player1_played = []
        self.player2_played = []
        
    def update(self, delta_time: float) -> None:
        # Update animations
        self.ui_manager.update_animations(delta_time)
        
        # Check win condition
        win_condition = self.combat_system.check_win_condition(self.player1, self.player2)
        if win_condition.game_over:
            self.next_scene = ('game_over', win_condition)
    
    def render(self) -> None:
        self.screen.fill(DARK_GRAY)
        
        # Render player labels
        self.ui_manager.render_player_label("AI Opponent", "top")
        self.ui_manager.render_player_label("You", "bottom")
        
        # Render player stats
        self.ui_manager.render_player_stats(self.player2, "top")
        self.ui_manager.render_player_stats(self.player1, "bottom")
        
        # Render round info
        phase_text = {
            'selection': 'Select 3 Cards',
            'queen_disable': '',
            'reveal': 'Cards Revealed - Press SPACE',
            'show_effects': '',
            'show_results': 'Round Complete - Press SPACE',
        }
        if self.round_phase == 'queen_disable':
            remaining = self.queen_disable_count - len(self.queen_disabled_indices)
            header = f"QUEEN: Click {remaining} opponent card(s) to disable"
            self.ui_manager.render_round_info(self.round_number, header)
        elif self.round_phase == 'show_effects' and self.effect_queue:
            idx = self.current_effect_index
            total = len(self.effect_queue)
            effect = self.effect_queue[idx]
            header = f"Effect {idx + 1}/{total}: {effect['text']} - Press SPACE"
            self.ui_manager.render_round_info(self.round_number, header)
        else:
            self.ui_manager.render_round_info(self.round_number, phase_text.get(self.round_phase, ''))
        
        # Render AI hand (face down during selection, revealed during resolution)
        if self.round_phase in ['show_effects', 'show_results'] and self.player2_played:
            self.render_ai_played_cards()
        elif self.round_phase == 'queen_disable' and self.player2_played:
            self.queen_card_rects = self._render_queen_disable_cards()
        elif self.round_phase == 'reveal' and self.player2_played:
            # Show cards face down during reveal phase
            self.render_ai_cards_face_down()
        else:
            self.render_ai_hand_placeholder()
        
        # Render player hand
        card_rects = self.ui_manager.render_hand(self.player1.hand, self.selected_cards, 
                                                 SCREEN_HEIGHT - 200)
        self.card_rects = card_rects
        
        # Render played cards in center
        if self.player1_played:
            # Show player cards face up after selection
            revealed = self.round_phase != 'selection'
            self.ui_manager.render_played_cards(self.player1_played, revealed, 'bottom')
        
        # Render combat summary if in results phase
        if self.round_phase == 'show_results':
            self.ui_manager.render_combat_summary(self.last_p1_damage, self.last_p2_damage, 
                                                  self.last_winner_id)
        
        # Render current effect highlight when stepping through effects
        if self.round_phase == 'show_effects' and self.effect_queue:
            self._render_current_effect()
        
        # Render animations
        self.ui_manager.render_animations()
        
        # Render instructions
        if self.round_phase == 'selection':
            self.render_instructions()
            self._render_card_tooltip()
    
    def render_ai_hand_placeholder(self) -> None:
        """Render placeholder for AI's hand (cards face down)."""
        card_width = 80
        card_height = 120
        spacing = 20
        y = 120
        
        # Show number of cards in AI hand
        num_cards = len(self.player2.hand)
        total_width = num_cards * (card_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i in range(num_cards):
            x = start_x + i * (card_width + spacing)
            rect = pygame.Rect(x, y, card_width, card_height)
            
            # Draw card back
            pygame.draw.rect(self.screen, self.ui_manager.BLUE, rect)
            pygame.draw.rect(self.screen, self.ui_manager.BLACK, rect, 2)
            
            # Draw pattern on card back
            for dy in range(0, card_height, 20):
                pygame.draw.line(self.screen, self.ui_manager.LIGHT_BLUE,
                               (x, y + dy), (x + card_width, y + dy), 1)
    
    def render_ai_played_cards(self) -> None:
        """Render AI's played cards (revealed)."""
        card_width = 100
        card_height = 140
        spacing = 30
        y = 250
        
        total_width = 3 * (card_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i, card in enumerate(self.player2_played):
            x = start_x + i * (card_width + spacing)
            self.ui_manager.render_card_with_details(card, x, y, card_width, card_height, 
                                                     show_abilities=True)
    
    def render_instructions(self) -> None:
        """Render instruction text."""
        if len(self.selected_cards) < 3:
            text = f"Select {3 - len(self.selected_cards)} more card(s)"
            color = self.ui_manager.YELLOW
        else:
            text = "Press SPACE to confirm"
            color = self.ui_manager.GREEN
        
        inst_text = self.ui_manager.font.render(text, True, color)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        
        # Add background
        bg_rect = inst_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, self.ui_manager.DARK_GRAY, bg_rect)
        
        self.screen.blit(inst_text, inst_rect)
    
    def handle_input(self, event: pygame.event.Event) -> None:
        # Track mouse position for hover tooltips
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        
        if self.round_phase == 'selection':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_card_selection(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and len(self.selected_cards) == 3:
                    self.confirm_selection()
        
        elif self.round_phase == 'queen_disable':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_queen_disable_click(event.pos)
        
        elif self.round_phase == 'reveal':
            # Press space to flip cards and start stepping through effects
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.resolve_round()
                if self.effect_queue:
                    self.round_phase = 'show_effects'
                    self.current_effect_index = 0
                else:
                    # No effects to show, skip straight to results
                    self.round_phase = 'show_results'
        
        elif self.round_phase == 'show_effects':
            # Press space to advance to the next effect
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.current_effect_index += 1
                if self.current_effect_index >= len(self.effect_queue):
                    self.round_phase = 'show_results'
        
        elif self.round_phase == 'show_results':
            # Press space to continue to next round
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.round_phase = 'selection'
                self.player1_played = []
                self.player2_played = []
                self.effect_queue = []
                self.current_effect_index = 0
                self.queen_disable_count = 0
                self.queen_disabled_indices = []
                self.queen_card_rects = []
                self.round_number += 1
    
    def handle_card_selection(self, pos: tuple) -> None:
        """Handle clicking on cards."""
        for i, rect in enumerate(self.card_rects):
            if rect.collidepoint(pos) and i < len(self.player1.hand):
                card = self.player1.hand[i]
                
                if card in self.selected_cards:
                    self.selected_cards.remove(card)
                elif len(self.selected_cards) < 3:
                    self.selected_cards.append(card)
                break
    
    def confirm_selection(self) -> None:
        """Confirm card selection and move to reveal or queen_disable phase."""
        # Player 1 plays selected cards
        self.player1_played = self.selected_cards.copy()
        for card in self.player1_played:
            self.player1.hand.remove(card)
        
        # AI plays random cards
        num_to_play = min(3, len(self.player2.hand))
        self.player2_played = random.sample(self.player2.hand, num_to_play)
        for card in self.player2_played:
            self.player2.hand.remove(card)
        
        self.selected_cards = []
        
        # Check if player 1 has a Queen
        p1_has_queen = any(c.rank == 'Q' for c in self.player1_played)
        
        if p1_has_queen and self.player2_played:
            # Determine how many cards the player can disable
            p1_vault = self.player1.vault.size()
            p2_vault = self.player2.vault.size()
            self.queen_disable_count = 2 if p1_vault < p2_vault else 1
            self.queen_disable_count = min(self.queen_disable_count, len(self.player2_played))
            self.queen_disabled_indices = []
            self.round_phase = 'queen_disable'
        else:
            # No Queen interaction needed, go straight to reveal
            self.round_phase = 'reveal'
    
    def resolve_round(self) -> None:
        """Resolve the round and build effect queue for step-by-step display."""
        self.effect_queue = []
        
        # Build queen_choices if player made selections
        queen_choices = None
        if self.queen_disabled_indices:
            queen_choices = {0: list(self.queen_disabled_indices)}
        
        # Resolve abilities
        ability_result = self.ability_resolver.resolve_abilities(
            self.player1, self.player2,
            self.player1_played, self.player2_played,
            self.player1.deck,
            queen_choices=queen_choices
        )
        
        # Build effect queue in the correct ability order:
        # Queen -> Ace -> Jack -> King -> Club -> Spade -> Diamond -> Heart
        all_played = self.player1_played + self.player2_played
        
        # Define the order: face cards by rank, then suits
        face_order = ['Q', 'A', 'J', 'K']
        suit_order = ['Club', 'Spade', 'Diamond', 'Heart']
        
        # First pass: face card abilities in order
        for target_rank in face_order:
            for idx, card in enumerate(all_played):
                if card.rank != target_rank:
                    continue
                is_p1_card = idx < len(self.player1_played)
                owner = self.player1 if is_p1_card else self.player2
                owner_label = "You" if is_p1_card else "AI"
                opponent = self.player2 if is_p1_card else self.player1

                if card.rank == 'Q':
                    msg = f"QUEEN: {owner_label} disables opponent abilities!"
                elif card.rank == 'A':
                    msg = "ACE: Undoes Queen + disables Jack & King!"
                elif card.rank == 'J':
                    msg = "JACK: Round logic reversed!"
                elif card.rank == 'K' and ability_result.king_activated:
                    opp_vault = opponent.vault.size()
                    msg = f"KING: {owner_label} deals {opp_vault} damage + vault reduced!"
                elif card.rank == 'K':
                    msg = f"KING: {owner_label} (no effect — disabled or no vault)"
                else:
                    continue

                if card.is_face_card():
                    self.effect_queue.append({
                        'text': msg,
                        'color': self.ui_manager._get_ability_color(card.rank),
                        'card': card,
                    })

        # Second pass: suit abilities in order (numbered cards only)
        for target_suit in suit_order:
            for idx, card in enumerate(all_played):
                if not card.is_numbered_card() or card.suit != target_suit:
                    continue
                is_p1_card = idx < len(self.player1_played)
                owner = self.player1 if is_p1_card else self.player2
                owner_label = "You" if is_p1_card else "AI"
                vault_size = owner.vault.size()

                if card.suit == 'Club':
                    bonus = vault_size // 2
                    msg = f"CLUB: {owner_label} +{bonus} damage (vault {vault_size})"
                elif card.suit == 'Spade':
                    bonus = vault_size // 2
                    msg = f"SPADE: {owner_label} +{bonus} defense (vault {vault_size})"
                elif card.suit == 'Diamond':
                    msg = "DIAMOND: Vault card removed!"
                elif card.suit == 'Heart':
                    bonus = vault_size // 4
                    msg = f"HEART: {owner_label} +{bonus} heal (vault {vault_size})"
                else:
                    continue

                self.effect_queue.append({
                    'text': msg,
                    'color': self.ui_manager._get_ability_color(card.suit),
                    'card': card,
                })
        
        # Calculate damage
        p1_base = self.combat_system.calculate_base_damage(self.player1_played)
        p2_base = self.combat_system.calculate_base_damage(self.player2_played)
        
        # Add ability bonuses
        p1_damage = p1_base + ability_result.damage_modifiers.get(0, 0)
        p2_damage = p2_base + ability_result.damage_modifiers.get(1, 0)
        
        # Determine winner (considering Jack reversal)
        winner_id = self.combat_system.determine_winner(p1_damage, p2_damage, 
                                                        ability_result.jack_count)
        
        # Store for display
        self.last_p1_damage = p1_damage
        self.last_p2_damage = p2_damage
        self.last_winner_id = winner_id
        
        # Calculate net damage (damage cancels point-for-point)
        net_damage = abs(p1_damage - p2_damage)
        
        # Add damage/winner effect to queue
        # determine_winner returns 1 for player1 (You), 2 for player2 (AI), None for tie
        if winner_id == 1:
            self.effect_queue.append({
                'text': f"You deal {net_damage} damage!",
                'color': self.ui_manager.GREEN,
                'card': None,
            })
        elif winner_id == 2:
            self.effect_queue.append({
                'text': f"AI deals {net_damage} damage to you!",
                'color': self.ui_manager.RED,
                'card': None,
            })
        else:
            self.effect_queue.append({
                'text': "Tied! Cards shuffled back.",
                'color': self.ui_manager.YELLOW,
                'card': None,
            })
        
        # Debug output
        print(f"\n=== Round {self.round_number} Resolution ===")
        print(f"Player 1 damage: {p1_damage}, Player 2 damage: {p2_damage}")
        print(f"Net damage: {net_damage}, Winner: {winner_id}")
        
        # Apply damage to loser
        # winner_id=1 means player1 (You) wins, winner_id=2 means player2 (AI) wins
        if winner_id == 1:
            self.combat_system.apply_damage(self.player2, net_damage, 0)
            self.combat_system.add_to_vault(self.player1, self.player1_played + self.player2_played)
            
            # Heart ability: heal winner
            for card in self.player1_played:
                if card.is_numbered_card() and card.suit == 'Heart':
                    heal_amount = self.player1.vault.size() // 4
                    self.player1.heal(heal_amount)
                    break
                    
        elif winner_id == 2:
            self.combat_system.apply_damage(self.player1, net_damage, 0)
            self.combat_system.add_to_vault(self.player2, self.player1_played + self.player2_played)
            
            # Heart ability: heal winner
            for card in self.player2_played:
                if card.is_numbered_card() and card.suit == 'Heart':
                    heal_amount = self.player2.vault.size() // 4
                    self.player2.heal(heal_amount)
                    break
        else:
            if self.player1.deck:
                self.player1.deck.add_cards(self.player1_played + self.player2_played)
                self.player1.deck.shuffle()
        
        # Draw new cards
        self.player1.draw_cards(3)
        self.player2.draw_cards(3)

    def _get_card_tooltip_lines(self, card) -> list:
        """Build tooltip description lines for a card based on current vault size."""
        vault_size = self.player1.vault.size()
        lines = [f"{card.rank} of {card.suit}s"]
        lines.append(f"Base damage: {card.get_base_damage()}")

        if card.is_face_card():
            if card.rank == 'A':
                lines.append("Ability: Undoes Queen effect")
                lines.append("+ disables Jack & King")
            elif card.rank == 'J':
                lines.append("Ability: Reverses round")
                lines.append("logic (lower damage wins)")
            elif card.rank == 'Q':
                p1v = vault_size
                p2v = self.player2.vault.size()
                count = 2 if p1v < p2v else 1
                lines.append(f"Ability: Disable {count} opponent")
                lines.append(f"card(s) (your vault {p1v} vs {p2v})")
            elif card.rank == 'K':
                opp_vault = self.player2.vault.size()
                reduction = opp_vault // 4
                lines.append(f"Ability: Deal {opp_vault} dmg")
                lines.append(f"+ remove {reduction} vault cards")
        else:
            if card.suit == 'Club':
                bonus = vault_size // 2
                lines.append(f"Ability: +{bonus} damage")
                lines.append(f"(vault {vault_size} / 2)")
            elif card.suit == 'Spade':
                bonus = vault_size // 2
                lines.append(f"Ability: +{bonus} defense")
                lines.append(f"(vault {vault_size} / 2)")
            elif card.suit == 'Heart':
                bonus = vault_size // 4
                lines.append(f"Ability: +{bonus} heal on win")
                lines.append(f"(vault {vault_size} / 4)")
            elif card.suit == 'Diamond':
                lines.append("Ability: Remove random card")
                lines.append("from any vault to draw pile")

        return lines

    def _render_card_tooltip(self) -> None:
        """Render a tooltip popup for the card under the mouse cursor."""
        if not hasattr(self, 'card_rects') or not self.card_rects:
            return

        # Find which card is hovered
        hovered_index = -1
        for i, rect in enumerate(self.card_rects):
            if rect.collidepoint(self.mouse_pos) and i < len(self.player1.hand):
                hovered_index = i
                break

        if hovered_index < 0:
            return

        card = self.player1.hand[hovered_index]
        lines = self._get_card_tooltip_lines(card)

        # Measure tooltip size
        font = self.ui_manager.font
        line_height = font.get_linesize()
        padding = 10
        max_width = max(font.size(line)[0] for line in lines)
        tooltip_w = max_width + padding * 2
        tooltip_h = line_height * len(lines) + padding * 2

        # Position tooltip above the hovered card
        card_rect = self.card_rects[hovered_index]
        tx = card_rect.centerx - tooltip_w // 2
        ty = card_rect.top - tooltip_h - 8

        # Clamp to screen bounds
        tx = max(4, min(tx, SCREEN_WIDTH - tooltip_w - 4))
        ty = max(4, ty)

        # Draw background
        bg_rect = pygame.Rect(tx, ty, tooltip_w, tooltip_h)
        pygame.draw.rect(self.screen, (20, 20, 30), bg_rect)
        pygame.draw.rect(self.screen, self.ui_manager.WHITE, bg_rect, 2)

        # Draw text lines
        for i, line in enumerate(lines):
            color = self.ui_manager.YELLOW if i == 0 else self.ui_manager.WHITE
            text_surface = font.render(line, True, color)
            self.screen.blit(text_surface, (tx + padding, ty + padding + i * line_height))

    def _render_queen_disable_cards(self) -> list:
        """Render opponent's face-down cards for Queen disable selection.
        Selected cards get a red highlight. Returns list of Rects for click detection."""
        card_width = 100
        card_height = 140
        spacing = 30
        y = 250

        num_cards = len(self.player2_played)
        total_width = num_cards * (card_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2

        rects = []
        for i in range(num_cards):
            x = start_x + i * (card_width + spacing)
            rect = pygame.Rect(x, y, card_width, card_height)
            rects.append(rect)

            # Draw card back
            pygame.draw.rect(self.screen, self.ui_manager.BLUE, rect)
            pygame.draw.rect(self.screen, self.ui_manager.BLACK, rect, 3)

            # Draw pattern
            for dy in range(0, card_height, 20):
                pygame.draw.line(self.screen, self.ui_manager.LIGHT_BLUE,
                                 (x, y + dy), (x + card_width, y + dy), 1)

            # Draw card number label
            label = self.ui_manager.font.render(str(i + 1), True, self.ui_manager.WHITE)
            label_rect = label.get_rect(center=(x + card_width // 2, y + card_height // 2))
            self.screen.blit(label, label_rect)

            # Highlight selected cards with red border
            if i in self.queen_disabled_indices:
                pygame.draw.rect(self.screen, self.ui_manager.RED, rect, 5)
                # Draw X over disabled card
                x_text = self.ui_manager.large_font.render("X", True, self.ui_manager.RED)
                x_rect = x_text.get_rect(center=(x + card_width // 2, y + card_height // 2))
                self.screen.blit(x_text, x_rect)

        return rects

    def _handle_queen_disable_click(self, pos: tuple) -> None:
        """Handle clicking on opponent's face-down cards during Queen disable phase."""
        for i, rect in enumerate(self.queen_card_rects):
            if rect.collidepoint(pos):
                if i in self.queen_disabled_indices:
                    # Deselect
                    self.queen_disabled_indices.remove(i)
                elif len(self.queen_disabled_indices) < self.queen_disable_count:
                    # Select
                    self.queen_disabled_indices.append(i)

                # Auto-advance when enough cards are selected
                if len(self.queen_disabled_indices) == self.queen_disable_count:
                    self.round_phase = 'reveal'
                break

    def _render_current_effect(self) -> None:
        """Render the current effect as a prominent banner in the center."""
        if not self.effect_queue or self.current_effect_index >= len(self.effect_queue):
            return
        
        effect = self.effect_queue[self.current_effect_index]
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2
        
        # Draw background panel
        panel_width = 600
        panel_height = 80
        panel_rect = pygame.Rect(
            center_x - panel_width // 2, center_y - panel_height // 2,
            panel_width, panel_height
        )
        pygame.draw.rect(self.screen, self.ui_manager.DARK_GRAY, panel_rect)
        pygame.draw.rect(self.screen, effect['color'], panel_rect, 3)
        
        # Draw effect text
        text_surface = self.ui_manager.large_font.render(effect['text'], True, effect['color'])
        text_rect = text_surface.get_rect(center=(center_x, center_y - 10))
        self.screen.blit(text_surface, text_rect)
        
        # Draw "Press SPACE" hint
        hint = self.ui_manager.font.render("Press SPACE to continue", True, self.ui_manager.GRAY)
        hint_rect = hint.get_rect(center=(center_x, center_y + 25))
        self.screen.blit(hint, hint_rect)

    def render_ai_cards_face_down(self) -> None:
        """Render AI's played cards face down in center area."""
        card_width = 100
        card_height = 140
        spacing = 30
        y = 250
        
        total_width = 3 * (card_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i in range(3):
            x = start_x + i * (card_width + spacing)
            rect = pygame.Rect(x, y, card_width, card_height)
            
            # Draw card back
            pygame.draw.rect(self.screen, self.ui_manager.BLUE, rect)
            pygame.draw.rect(self.screen, self.ui_manager.BLACK, rect, 3)
            
            # Draw pattern on card back
            for dy in range(0, card_height, 20):
                pygame.draw.line(self.screen, self.ui_manager.LIGHT_BLUE,
                               (x, y + dy), (x + card_width, y + dy), 1)
