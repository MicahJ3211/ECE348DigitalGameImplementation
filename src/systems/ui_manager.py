import pygame
from typing import List, Optional
from src.entities.player import Player
from src.entities.card import Card


class UIManager:
    """Manages rendering of game UI elements."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize UI manager with screen surface.
        
        Args:
            screen: The pygame surface to render to
        """
        self.screen = screen
        self.font = None
        self.large_font = None
        
        # Initialize fonts with fallback
        try:
            self.font = pygame.font.Font(None, 32)
            self.large_font = pygame.font.Font(None, 48)
        except:
            # Fallback to default font
            self.font = pygame.font.SysFont('arial', 32)
            self.large_font = pygame.font.SysFont('arial', 48)
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 100, 255)
        self.GRAY = (128, 128, 128)
        self.YELLOW = (255, 255, 0)
        self.DARK_GRAY = (50, 50, 50)
        self.LIGHT_BLUE = (173, 216, 230)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)
        
        # Card colors by suit
        self.SUIT_COLORS = {
            'Club': (0, 128, 0),      # Green
            'Spade': (0, 0, 0),        # Black
            'Heart': (255, 0, 0),      # Red
            'Diamond': (255, 100, 0)   # Orange
        }
        
        # Animation state
        self.animations = []
        self.animation_messages = []
    
    def render_player_stats(self, player: Player, position: str) -> None:
        """
        Render player statistics (health, defense, vault size).
        
        Args:
            player: The player to render stats for
            position: 'top' or 'bottom' for screen position
        """
        y_offset = 20 if position == 'top' else self.screen.get_height() - 80
        x_offset = 20
        
        # Render health bar
        health_text = self.font.render(f"Health: {player.health}/50", True, self.WHITE)
        self.screen.blit(health_text, (x_offset, y_offset))
        
        # Health bar background
        bar_width = 200
        bar_height = 20
        bar_x = x_offset + 150
        bar_y = y_offset + 5
        
        pygame.draw.rect(self.screen, self.GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar fill
        health_ratio = player.health / 50
        fill_width = int(bar_width * health_ratio)
        health_color = self.GREEN if health_ratio > 0.5 else (self.YELLOW if health_ratio > 0.25 else self.RED)
        pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, fill_width, bar_height))
        
        # Render defense
        defense_text = self.font.render(f"Defense: {player.defense}", True, self.BLUE)
        self.screen.blit(defense_text, (x_offset + 400, y_offset))
        
        # Render vault size
        vault_text = self.font.render(f"Vault: {player.vault.size()}", True, self.YELLOW)
        self.screen.blit(vault_text, (x_offset + 600, y_offset))
    
    def render_hand(self, cards: List[Card], selected: List[Card], y_position: int) -> List[pygame.Rect]:
        """
        Render player's hand of cards.
        
        Args:
            cards: List of cards in hand
            selected: List of selected cards
            y_position: Y position to render at
            
        Returns:
            List of Rect objects for card positions (for click detection)
        """
        card_rects = []
        card_width = 80
        card_height = 120
        spacing = 20
        
        # Center the hand
        total_width = len(cards) * (card_width + spacing) - spacing
        start_x = (self.screen.get_width() - total_width) // 2
        
        for i, card in enumerate(cards):
            x = start_x + i * (card_width + spacing)
            y = y_position
            
            # Raise selected cards
            if card in selected:
                y -= 20
            
            rect = pygame.Rect(x, y, card_width, card_height)
            card_rects.append(rect)
            
            # Draw card background
            color = self.SUIT_COLORS.get(card.suit, self.WHITE)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2)
            
            # Draw card rank
            rank_text = self.font.render(card.rank, True, self.WHITE if card.suit in ['Club', 'Spade'] else self.BLACK)
            rank_rect = rank_text.get_rect(center=(x + card_width // 2, y + 30))
            self.screen.blit(rank_text, rank_rect)
            
            # Draw suit symbol
            suit_text = self.font.render(card.suit[0], True, self.WHITE if card.suit in ['Club', 'Spade'] else self.BLACK)
            suit_rect = suit_text.get_rect(center=(x + card_width // 2, y + 70))
            self.screen.blit(suit_text, suit_rect)
            
            # Highlight if selected
            if card in selected:
                pygame.draw.rect(self.screen, self.YELLOW, rect, 4)
        
        return card_rects
    
    def render_played_cards(self, cards: List[Card], revealed: bool, position: str) -> None:
        """
        Render played cards in the center area.
        
        Args:
            cards: List of 3 cards played
            revealed: Whether cards are face-up
            position: 'top' or 'bottom' for which player
        """
        card_width = 80
        card_height = 120
        spacing = 20
        
        # Position in center
        total_width = 3 * (card_width + spacing) - spacing
        start_x = (self.screen.get_width() - total_width) // 2
        y = 200 if position == 'top' else 350
        
        for i, card in enumerate(cards):
            x = start_x + i * (card_width + spacing)
            rect = pygame.Rect(x, y, card_width, card_height)
            
            if revealed:
                # Draw revealed card
                color = self.SUIT_COLORS.get(card.suit, self.WHITE)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, self.BLACK, rect, 2)
                
                rank_text = self.font.render(card.rank, True, self.WHITE if card.suit in ['Club', 'Spade'] else self.BLACK)
                rank_rect = rank_text.get_rect(center=(x + card_width // 2, y + 40))
                self.screen.blit(rank_text, rank_rect)
                
                suit_text = self.font.render(card.suit[0], True, self.WHITE if card.suit in ['Club', 'Spade'] else self.BLACK)
                suit_rect = suit_text.get_rect(center=(x + card_width // 2, y + 80))
                self.screen.blit(suit_text, suit_rect)
            else:
                # Draw card back
                pygame.draw.rect(self.screen, self.BLUE, rect)
                pygame.draw.rect(self.screen, self.BLACK, rect, 2)
    
    def render_round_info(self, round_num: int, phase: str) -> None:
        """
        Render round number and current phase.
        
        Args:
            round_num: Current round number
            phase: Current phase (e.g., 'Selection', 'Reveal', 'Resolution')
        """
        info_text = self.large_font.render(f"Round {round_num} - {phase}", True, self.WHITE)
        info_rect = info_text.get_rect(center=(self.screen.get_width() // 2, 50))
        self.screen.blit(info_text, info_rect)
    
    def show_ability_animation(self, ability: str, target: Player, source_card: Card = None) -> None:
        """
        Show ability activation animation with visual effects.
        
        Args:
            ability: Name of the ability (rank or suit)
            target: Target player
            source_card: The card that triggered the ability
        """
        # Create animation message
        ability_messages = {
            'A': "ACE: Face abilities disabled!",
            'J': "JACK: Round logic reversed!",
            'Q': "QUEEN: Opponent abilities disabled!",
            'K': "KING: Damage dealt!",
            'Club': "CLUB: Damage bonus!",
            'Spade': "SPADE: Defense bonus!",
            'Heart': "HEART: Healing!",
            'Diamond': "DIAMOND: Vault card removed!"
        }
        
        message = ability_messages.get(ability, f"{ability} activated!")
        
        # Add to animation queue with timer
        self.animation_messages.append({
            'text': message,
            'timer': 120,  # frames to display
            'color': self._get_ability_color(ability),
            'y_offset': len(self.animation_messages) * 40
        })
    
    def _get_ability_color(self, ability: str) -> tuple:
        """Get color for ability animation."""
        colors = {
            'A': self.PURPLE,
            'J': self.ORANGE,
            'Q': self.PURPLE,
            'K': self.RED,
            'Club': self.GREEN,
            'Spade': self.BLUE,
            'Heart': self.RED,
            'Diamond': self.ORANGE
        }
        return colors.get(ability, self.WHITE)
    
    def update_animations(self, delta_time: float) -> None:
        """Update animation timers."""
        # Update message timers
        self.animation_messages = [
            msg for msg in self.animation_messages
            if msg['timer'] > 0
        ]
        
        for msg in self.animation_messages:
            msg['timer'] -= 1
    
    def render_animations(self) -> None:
        """Render active animations."""
        center_x = self.screen.get_width() // 2
        start_y = self.screen.get_height() // 2 - 100
        
        for i, msg in enumerate(self.animation_messages):
            # Fade effect
            alpha = min(255, msg['timer'] * 2)
            
            # Create text surface
            text = self.large_font.render(msg['text'], True, msg['color'])
            text_rect = text.get_rect(center=(center_x, start_y + i * 50))
            
            # Add background for readability
            bg_rect = text_rect.inflate(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.fill(self.DARK_GRAY)
            bg_surface.set_alpha(200)
            
            self.screen.blit(bg_surface, bg_rect)
            self.screen.blit(text, text_rect)
    
    def render_damage_numbers(self, damage: int, position: tuple, is_true_damage: bool = False) -> None:
        """
        Render floating damage numbers.
        
        Args:
            damage: Amount of damage
            position: (x, y) position to display
            is_true_damage: Whether this is true damage (different color)
        """
        color = self.PURPLE if is_true_damage else self.RED
        damage_text = self.large_font.render(f"-{damage}", True, color)
        text_rect = damage_text.get_rect(center=position)
        
        # Add outline for visibility
        outline_text = self.large_font.render(f"-{damage}", True, self.BLACK)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            self.screen.blit(outline_text, text_rect.move(dx, dy))
        
        self.screen.blit(damage_text, text_rect)

    def render_player_label(self, player_name: str, position: str) -> None:
        """
        Render player name label.
        
        Args:
            player_name: Name to display (e.g., "You", "AI Opponent")
            position: 'top' or 'bottom'
        """
        y = 100 if position == 'top' else self.screen.get_height() - 200
        label_text = self.large_font.render(player_name, True, self.YELLOW)
        label_rect = label_text.get_rect(center=(self.screen.get_width() // 2, y))
        
        # Add background
        bg_rect = label_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, self.DARK_GRAY, bg_rect)
        pygame.draw.rect(self.screen, self.YELLOW, bg_rect, 2)
        
        self.screen.blit(label_text, label_rect)
    
    def render_card_with_details(self, card: Card, x: int, y: int, width: int, height: int, 
                                 show_abilities: bool = False) -> pygame.Rect:
        """
        Render a single card with detailed information.
        
        Args:
            card: The card to render
            x, y: Position
            width, height: Card dimensions
            show_abilities: Whether to show ability icons
            
        Returns:
            Rect of the rendered card
        """
        rect = pygame.Rect(x, y, width, height)
        
        # Draw card background with gradient effect
        color = self.SUIT_COLORS.get(card.suit, self.WHITE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.BLACK, rect, 3)
        
        # Draw rank (larger)
        rank_text = self.large_font.render(card.rank, True, 
                                          self.WHITE if card.suit in ['Club', 'Spade'] else self.BLACK)
        rank_rect = rank_text.get_rect(center=(x + width // 2, y + height // 3))
        self.screen.blit(rank_text, rank_rect)
        
        # Draw suit name
        suit_text = self.font.render(card.suit, True, 
                                     self.WHITE if card.suit in ['Club', 'Spade'] else self.BLACK)
        suit_rect = suit_text.get_rect(center=(x + width // 2, y + 2 * height // 3))
        self.screen.blit(suit_text, suit_rect)
        
        # Show ability indicator if requested
        if show_abilities:
            if card.is_face_card():
                ability_icon = self.font.render("★", True, self.YELLOW)
            elif card.is_numbered_card():
                ability_icon = self.font.render("◆", True, self.LIGHT_BLUE)
            else:
                ability_icon = None
            
            if ability_icon:
                icon_rect = ability_icon.get_rect(topright=(x + width - 5, y + 5))
                self.screen.blit(ability_icon, icon_rect)
        
        return rect
    
    def render_combat_summary(self, p1_damage: int, p2_damage: int, winner_id: int = None) -> None:
        """
        Render combat summary showing damage dealt.
        
        Args:
            p1_damage: Player 1's damage
            p2_damage: Player 2's damage
            winner_id: ID of winner (1 or 2), None for tie
        """
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2
        
        # Draw background panel
        panel_width = 400
        panel_height = 150
        panel_rect = pygame.Rect(center_x - panel_width // 2, center_y - panel_height // 2,
                                 panel_width, panel_height)
        pygame.draw.rect(self.screen, self.DARK_GRAY, panel_rect)
        pygame.draw.rect(self.screen, self.WHITE, panel_rect, 3)
        
        # Draw damage values
        p1_text = self.large_font.render(f"You: {p1_damage} dmg", True, self.GREEN)
        p2_text = self.large_font.render(f"AI: {p2_damage} dmg", True, self.RED)
        
        self.screen.blit(p1_text, (center_x - panel_width // 2 + 20, center_y - 40))
        self.screen.blit(p2_text, (center_x - panel_width // 2 + 20, center_y + 10))
        
        # Draw winner indicator
        if winner_id is not None:
            winner_text = "YOU WIN!" if winner_id == 1 else "AI WINS!"
            winner_color = self.GREEN if winner_id == 1 else self.RED
            winner_render = self.large_font.render(winner_text, True, winner_color)
            winner_rect = winner_render.get_rect(center=(center_x, center_y + 60))
            self.screen.blit(winner_render, winner_rect)
        else:
            tie_text = self.large_font.render("TIE!", True, self.YELLOW)
            tie_rect = tie_text.get_rect(center=(center_x, center_y + 60))
            self.screen.blit(tie_text, tie_rect)
