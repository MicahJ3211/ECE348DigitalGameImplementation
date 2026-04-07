from dataclasses import dataclass
from typing import Optional


@dataclass
class Card:
    """Represents a playing card with rank and suit."""
    rank: str  # 'A', '2'-'10', 'J', 'Q', 'K'
    suit: str  # 'Club', 'Spade', 'Heart', 'Diamond'
    
    def get_base_damage(self) -> int:
        """
        Returns base damage based on card rank.
        Ace = 1, numbered cards = rank value, face cards = 10
        """
        if self.rank == 'A':
            return 1
        elif self.rank in ['J', 'Q', 'K']:
            return 10
        else:
            return int(self.rank)
    
    def is_face_card(self) -> bool:
        """Returns True if card is a face card (A, J, Q, K)."""
        return self.rank in ['A', 'J', 'Q', 'K']
    
    def is_numbered_card(self) -> bool:
        """Returns True if card is numbered (2-10)."""
        return self.rank not in ['A', 'J', 'Q', 'K']
    
    def get_suit_ability(self) -> Optional[str]:
        """
        Returns suit ability name if numbered card, None if face card.
        Face cards do NOT trigger suit abilities.
        """
        if self.is_numbered_card():
            return self.suit
        return None
    
    def get_face_ability(self) -> Optional[str]:
        """Returns face ability name if face card, None otherwise."""
        if self.is_face_card():
            return self.rank
        return None
    
    def __str__(self) -> str:
        """String representation of the card."""
        return f"{self.rank} of {self.suit}s"
    
    def __repr__(self) -> str:
        """Repr representation of the card."""
        return f"Card(rank='{self.rank}', suit='{self.suit}')"
