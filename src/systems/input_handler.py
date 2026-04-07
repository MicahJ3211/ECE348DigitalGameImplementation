import pygame
from typing import List, Optional, Tuple
from src.entities.card import Card


class InputHandler:
    """Handles mouse input for card selection and game interactions."""
    
    def __init__(self):
        """Initialize input handler."""
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.selected_cards: List[Card] = []
        self.selection_locked: bool = False
        self.input_blocked: bool = False
    
    def handle_event(self, event: pygame.event.Event, scene) -> None:
        """
        Process pygame events.
        
        Args:
            event: The pygame event to process
            scene: The current scene (for context-specific handling)
        """
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Delegate to scene for specific handling
                if hasattr(scene, 'handle_click'):
                    scene.handle_click(self.mouse_pos)
    
    def get_hovered_card(self, mouse_pos: Tuple[int, int], cards: List[Card], 
                        card_positions: List[pygame.Rect]) -> Optional[Card]:
        """
        Get the card currently under the mouse cursor.
        
        Args:
            mouse_pos: Current mouse position (x, y)
            cards: List of cards to check
            card_positions: List of Rect objects for card positions
            
        Returns:
            Card if mouse is over a card, None otherwise
        """
        for i, rect in enumerate(card_positions):
            if rect.collidepoint(mouse_pos):
                return cards[i]
        return None
    
    def is_valid_selection(self, selected_cards: List[Card], hand: List[Card]) -> bool:
        """
        Validate if the current selection is valid.
        
        Args:
            selected_cards: List of currently selected cards
            hand: Player's hand
            
        Returns:
            bool: True if selection is valid (exactly 3 cards from hand)
        """
        # Must have exactly 3 cards
        if len(selected_cards) != 3:
            return False
        
        # All selected cards must be in hand
        for card in selected_cards:
            if card not in hand:
                return False
        
        return True
    
    def lock_selection(self) -> None:
        """Lock the current selection (prevent modifications)."""
        self.selection_locked = True
    
    def unlock_selection(self) -> None:
        """Unlock selection (allow modifications)."""
        self.selection_locked = False
    
    def block_input(self) -> None:
        """Block all input (during animations or opponent turn)."""
        self.input_blocked = True
    
    def unblock_input(self) -> None:
        """Unblock input."""
        self.input_blocked = False
    
    def reset(self) -> None:
        """Reset input handler state."""
        self.selected_cards = []
        self.selection_locked = False
        self.input_blocked = False
