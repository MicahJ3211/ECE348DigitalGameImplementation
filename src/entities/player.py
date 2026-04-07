from dataclasses import dataclass, field
from typing import List, Optional
from .vault import Vault
from .deck import Deck


@dataclass
class Player:
    """Represents a player with health, defense, vault, hand, and deck."""
    player_id: int
    health: int = 50
    defense: int = 0
    vault: Vault = field(default_factory=Vault)
    hand: List = field(default_factory=list)
    deck: Optional[Deck] = None
    
    def take_damage(self, standard_dmg: int, true_dmg: int) -> None:
        """
        Apply damage to player. Defense blocks standard damage first,
        then remaining damage reduces health. True damage bypasses defense.
        """
        # Apply standard damage (blocked by defense)
        if standard_dmg > 0:
            if standard_dmg <= self.defense:
                self.defense -= standard_dmg
            else:
                remaining_dmg = standard_dmg - self.defense
                self.defense = 0
                self.health -= remaining_dmg
        
        # Apply true damage (bypasses defense)
        if true_dmg > 0:
            self.health -= true_dmg
        
        # Ensure health doesn't go negative
        self.health = max(0, self.health)
    
    def heal(self, amount: int) -> None:
        """Increase health, capped at 50."""
        self.health = min(50, self.health + amount)
    
    def add_defense(self, amount: int) -> None:
        """Increase defense value."""
        self.defense += amount
    
    def decay_defense(self) -> None:
        """Reduce defense by floor(defense / 4)."""
        decay_amount = self.defense // 4
        self.defense -= decay_amount
    
    def draw_cards(self, count: int) -> None:
        """Draw cards from deck to hand."""
        if self.deck:
            drawn = self.deck.draw(count)
            self.hand.extend(drawn)
    
    def shed_card(self, bonus_type: str) -> None:
        """
        Remove random vault card and apply bonus.
        bonus_type: 'damage', 'defense', or 'health'
        """
        card = self.vault.remove_random_card()
        if card is None:
            return  # No cards to shed
        
        # Bonus is applied by the caller (Combat_System)
        # This method just removes the card from vault
    
    def __repr__(self) -> str:
        return f"Player(id={self.player_id}, health={self.health}, defense={self.defense}, vault_size={self.vault.size()}, hand_size={len(self.hand)})"
