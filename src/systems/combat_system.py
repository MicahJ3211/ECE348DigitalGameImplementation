from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RoundResult:
    """Result of a round resolution."""
    winner_id: Optional[int]  # None for tie
    p1_standard_damage: int
    p2_standard_damage: int
    p1_true_damage: int
    p2_true_damage: int
    played_cards: List  # All 6 cards
    abilities_activated: List[str] = field(default_factory=list)


@dataclass
class WinCondition:
    """Game win condition status."""
    game_over: bool
    winner_id: Optional[int]  # None for tie
    reason: str  # 'health', 'vault', 'tie'


class CombatSystem:
    """Resolves rounds, calculates damage, determines winners."""
    
    def __init__(self):
        pass
    
    def calculate_base_damage(self, cards: List) -> int:
        """Sum base damage from cards."""
        total = 0
        for card in cards:
            total += card.get_base_damage()
        return total
    
    def apply_damage(self, player, standard_dmg: int, true_dmg: int) -> None:
        """Apply damage to player."""
        player.take_damage(standard_dmg, true_dmg)
    
    def determine_winner(self, p1_damage: int, p2_damage: int, jack_count: int) -> Optional[int]:
        """
        Determine round winner based on damage.
        jack_count: number of Jacks played (odd = reversed logic)
        Returns: 1 for player 1, 2 for player 2, None for tie
        """
        reversed_logic = (jack_count % 2) == 1
        
        if p1_damage == p2_damage:
            return None  # Tie
        
        if reversed_logic:
            # Lower damage wins
            return 1 if p1_damage < p2_damage else 2
        else:
            # Higher damage wins
            return 1 if p1_damage > p2_damage else 2
    
    def add_to_vault(self, player, cards: List) -> None:
        """Add cards to player's vault."""
        player.vault.add_cards(cards)
    
    def check_win_condition(self, player1, player2) -> WinCondition:
        """Check if game is over and determine winner."""
        # Check health-based win
        if player1.health <= 0 and player2.health <= 0:
            return WinCondition(game_over=True, winner_id=None, reason='tie')
        elif player1.health <= 0:
            return WinCondition(game_over=True, winner_id=2, reason='health')
        elif player2.health <= 0:
            return WinCondition(game_over=True, winner_id=1, reason='health')
        
        # Check if players can play a full round
        if player1.deck and player2.deck:
            p1_can_play = len(player1.hand) >= 3 or player1.deck.can_draw(3 - len(player1.hand))
            p2_can_play = len(player2.hand) >= 3 or player2.deck.can_draw(3 - len(player2.hand))
            
            if not (p1_can_play and p2_can_play):
                # Vault-based win
                if player1.vault.size() > player2.vault.size():
                    return WinCondition(game_over=True, winner_id=1, reason='vault')
                elif player2.vault.size() > player1.vault.size():
                    return WinCondition(game_over=True, winner_id=2, reason='vault')
                else:
                    return WinCondition(game_over=True, winner_id=None, reason='tie')
        
        return WinCondition(game_over=False, winner_id=None, reason='')
    
    def resolve_round(self, player1, player2, cards1: List, cards2: List) -> RoundResult:
        """
        Resolve a complete round.
        This is a simplified version - full implementation requires Ability_Resolver integration.
        """
        # Calculate base damage
        p1_base = self.calculate_base_damage(cards1)
        p2_base = self.calculate_base_damage(cards2)
        
        # For now, just use base damage (abilities will be added via Ability_Resolver)
        p1_damage = p1_base
        p2_damage = p2_base
        
        # Determine winner (no Jack logic yet)
        winner_id = self.determine_winner(p1_damage, p2_damage, 0)
        
        # Create result
        all_cards = cards1 + cards2
        result = RoundResult(
            winner_id=winner_id,
            p1_standard_damage=p1_damage,
            p2_standard_damage=p2_damage,
            p1_true_damage=0,
            p2_true_damage=0,
            played_cards=all_cards
        )
        
        return result
