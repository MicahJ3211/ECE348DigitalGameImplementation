import random
from typing import List


class Deck:
    """Manages the draw pile of cards."""
    
    def __init__(self, cards: List):
        self._cards: List = list(cards)
    
    def shuffle(self) -> None:
        """Randomize card order."""
        random.shuffle(self._cards)
    
    def draw(self, count: int) -> List:
        """
        Remove and return top count cards.
        Returns fewer cards if not enough available.
        """
        drawn = []
        for _ in range(min(count, len(self._cards))):
            if self._cards:
                drawn.append(self._cards.pop(0))
        return drawn
    
    def add_cards(self, cards: List) -> None:
        """Add cards to bottom of deck (for tied rounds)."""
        self._cards.extend(cards)
    
    def remaining(self) -> int:
        """Return number of cards left in deck."""
        return len(self._cards)
    
    def can_draw(self, count: int) -> bool:
        """Return True if count cards are available."""
        return len(self._cards) >= count
    
    def __repr__(self) -> str:
        return f"Deck(remaining={self.remaining()})"
