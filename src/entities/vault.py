import random
from typing import List, Optional


class Vault:
    """Storage for won cards that powers various abilities."""
    
    def __init__(self):
        self._cards: List = []
    
    def add_cards(self, cards: List) -> None:
        """Add cards to the vault."""
        self._cards.extend(cards)
    
    def remove_random_card(self) -> Optional:
        """
        Remove and return a random card from the vault.
        Returns None if vault is empty.
        """
        if self.is_empty():
            return None
        card = random.choice(self._cards)
        self._cards.remove(card)
        return card
    
    def remove_cards_from_game(self, count: int) -> List:
        """
        Remove count cards permanently (for King ability).
        Returns list of removed cards.
        """
        removed = []
        for _ in range(min(count, len(self._cards))):
            if self._cards:
                card = random.choice(self._cards)
                self._cards.remove(card)
                removed.append(card)
        return removed
    
    def size(self) -> int:
        """Return number of cards in vault."""
        return len(self._cards)
    
    def is_empty(self) -> bool:
        """Return True if vault has no cards."""
        return len(self._cards) == 0
    
    def __repr__(self) -> str:
        return f"Vault(size={self.size()})"
