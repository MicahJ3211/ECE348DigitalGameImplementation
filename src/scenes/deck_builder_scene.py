import pygame
from typing import List
from .scene import Scene
from src.entities.card import Card
from src.systems.deck_builder import DeckBuilder


class DeckBuilderScene(Scene):
    """Scene for deck construction phase."""
    
    def __init__(self, game_engine):
        """
        Initialize deck builder scene.
        
        Args:
            game_engine: Reference to the main game engine
        """
        super().__init__(game_engine)
        self.deck_builder = DeckBuilder()
        self.current_player = 0  # 0 or 1
        self.available_cards = self._create_full_deck()
        self.card_rects = []
        
        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.GREEN = (0, 255, 0)
    
    def _create_full_deck(self) -> List[Card]:
        """Create a full 52-card deck."""
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        suits = ['Club', 'Spade', 'Heart', 'Diamond']
        
        cards = []
        for suit in suits:
            for rank in ranks:
                cards.append(Card(rank=rank, suit=suit))
        
        return cards
    
    def update(self, delta_time: float) -> None:
        """
        Update scene state.
        
        Args:
            delta_time: Time since last frame in seconds
        """
        # Check if both players have completed selection
        if self.deck_builder.is_selection_complete():
            # Transition to gameplay scene
            if hasattr(self.game_engine, 'scene_manager'):
                self.game_engine.scene_manager.change_scene('gameplay', 
                                                           deck_builder=self.deck_builder)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the deck builder scene.
        
        Args:
            screen: The pygame surface to render to
        """
        screen.fill(self.BLACK)
        
        # Render title
        title_text = self.font.render(f"Player {self.current_player + 1} - Select 26 Cards", 
                                     True, self.WHITE)
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 30))
        screen.blit(title_text, title_rect)
        
        # Render selection count
        selected_count = len(self.deck_builder.player_selections[self.current_player])
        count_text = self.small_font.render(f"Selected: {selected_count}/26", True, self.WHITE)
        screen.blit(count_text, (20, 70))
        
        # Render available cards in a grid
        self.card_rects = []
        card_width = 60
        card_height = 90
        spacing = 10
        cards_per_row = 13
        
        start_x = 50
        start_y = 120
        
        for i, card in enumerate(self.available_cards):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = start_x + col * (card_width + spacing)
            y = start_y + row * (card_height + spacing)
            
            rect = pygame.Rect(x, y, card_width, card_height)
            self.card_rects.append(rect)
            
            # Check if card is already selected
            card_id = f"{card.rank}_{card.suit}"
            is_selected = card_id in self.deck_builder.selected_cards
            
            # Draw card
            if is_selected:
                pygame.draw.rect(screen, self.GRAY, rect)
            else:
                color = self._get_suit_color(card.suit)
                pygame.draw.rect(screen, color, rect)
            
            pygame.draw.rect(screen, self.WHITE, rect, 2)
            
            # Draw rank
            rank_text = self.small_font.render(card.rank, True, self.WHITE)
            rank_rect = rank_text.get_rect(center=(x + card_width // 2, y + 30))
            screen.blit(rank_text, rank_rect)
            
            # Draw suit initial
            suit_text = self.small_font.render(card.suit[0], True, self.WHITE)
            suit_rect = suit_text.get_rect(center=(x + card_width // 2, y + 60))
            screen.blit(suit_text, suit_rect)
        
        # Render instructions
        if selected_count < 26:
            inst_text = self.small_font.render("Click cards to select them", True, self.WHITE)
        else:
            inst_text = self.small_font.render("Press SPACE to confirm selection", True, self.GREEN)
        
        inst_rect = inst_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
        screen.blit(inst_text, inst_rect)
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """
        Handle input events.
        
        Args:
            event: The pygame event to handle
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # Check if a card was clicked
            for i, rect in enumerate(self.card_rects):
                if rect.collidepoint(mouse_pos):
                    card = self.available_cards[i]
                    self.deck_builder.select_card(self.current_player, card)
                    break
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Confirm selection if 26 cards selected
                selected_count = len(self.deck_builder.player_selections[self.current_player])
                if selected_count == 26:
                    if self.current_player == 0:
                        # Move to player 2
                        self.current_player = 1
                    else:
                        # Both players done, scene will transition in update()
                        pass
    
    def _get_suit_color(self, suit: str) -> tuple:
        """Get color for a suit."""
        colors = {
            'Club': (0, 128, 0),
            'Spade': (0, 0, 0),
            'Heart': (200, 0, 0),
            'Diamond': (200, 100, 0)
        }
        return colors.get(suit, (100, 100, 100))
