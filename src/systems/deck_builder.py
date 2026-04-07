from typing import Dict, List, Set
from src.entities.card import Card
from src.entities.deck import Deck


class DeckBuilder:
    """Manages deck construction phase where players select cards."""
    
    def __init__(self):
        """Initialize deck builder with empty selections."""
        self.player_selections: Dict[int, List[Card]] = {0: [], 1: []}
        self.selected_cards: Set[str] = set()  # Track selected card identifiers
    
    def select_card(self, player_id: int, card: Card) -> bool:
        """
        Select a card for a player's deck.
        
        Args:
            player_id: The player ID (0 or 1)
            card: The card to select
            
        Returns:
            bool: True if selection successful, False if invalid
        """
        # Validate player ID
        if player_id not in [0, 1]:
            return False
        
        # Check if player already has 26 cards
        if len(self.player_selections[player_id]) >= 26:
            return False
        
        # Create unique identifier for the card
        card_id = f"{card.rank}_{card.suit}"
        
        # Check if card already selected by either player
        if card_id in self.selected_cards:
            return False
        
        # Add card to player's selection
        self.player_selections[player_id].append(card)
        self.selected_cards.add(card_id)
        return True
    
    def is_selection_complete(self) -> bool:
        """
        Check if both players have completed their selections.
        
        Returns:
            bool: True if both players have 26 cards each
        """
        return (len(self.player_selections[0]) == 26 and 
                len(self.player_selections[1]) == 26)
    
    def create_game_deck(self) -> Deck:
        """
        Combine both players' selections into a single shuffled deck.
        
        Returns:
            Deck: A shuffled 52-card deck
        """
        if not self.is_selection_complete():
            raise ValueError("Both players must select 26 cards before creating game deck")
        
        # Combine all cards
        all_cards = self.player_selections[0] + self.player_selections[1]
        
        # Create and shuffle deck
        deck = Deck(all_cards)
        deck.shuffle()
        return deck
    
    def deal_initial_hands(self, deck: Deck, players: List) -> None:
        """
        Deal 6 cards to each player from the deck.
        
        Args:
            deck: The game deck to deal from
            players: List of Player objects [player1, player2]
        """
        for player in players:
            player.draw_cards(6)
