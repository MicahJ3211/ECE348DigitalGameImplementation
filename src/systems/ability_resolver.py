from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class AbilityResult:
    """Result of ability resolution containing all modifiers and flags."""
    damage_modifiers: Dict[int, int]  # player_id -> damage bonus
    defense_modifiers: Dict[int, int]  # player_id -> defense bonus
    disabled_abilities: Dict[int, List[int]]  # player_id -> card indices
    jack_count: int  # Number of Jacks played
    king_activated: bool


class AbilityResolver:
    """Resolves card abilities in the correct order of operations."""
    
    def __init__(self, combat_system):
        """
        Initialize with reference to Combat_System.
        
        Args:
            combat_system: The Combat_System instance for applying effects
        """
        self.combat_system = combat_system
    
    def resolve_abilities(self, player1, player2, cards1: List, cards2: List, draw_pile=None, queen_choices=None) -> AbilityResult:
        """
        Main method to resolve all abilities in correct order.
        
        Order of operations:
        1. Queen (disable opponent abilities)
        2. Ace (disable remaining face card abilities: J, K)
        3. Jack (reverse round logic)
        4. King (damage + vault reduction)
        5. Club (damage bonus)
        6. Spade (defense bonus)
        7. Diamond (vault manipulation)
        8. Heart (healing, post-winner — handled separately)
        
        Args:
            player1: First player
            player2: Second player
            cards1: Player 1's 3 cards
            cards2: Player 2's 3 cards
            draw_pile: Optional draw pile for Diamond ability
            queen_choices: Optional dict mapping player_index -> list of opponent card indices
                          the player chose to disable via Queen ability
            
        Returns:
            AbilityResult with all modifiers and flags
        """
        players = [player1, player2]
        cards = [cards1, cards2]
        
        # Initialize result tracking
        disabled_abilities = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}
        
        # 1. Queen (disable opponent abilities)
        queen_disabled = self._execute_queen(players, cards, disabled_abilities, queen_choices)
        
        # 2. Ace (disable J/K abilities, undo Queen's disables)
        self._execute_ace(players, cards, disabled_abilities, queen_disabled)
        
        # 3. Jack (count for reversal)
        jack_count = self._execute_jack(players, cards, disabled_abilities)
        
        # 4. King (damage + vault reduction)
        king_activated = self._execute_king(players, cards, disabled_abilities)
        
        # 5. Club (damage bonus)
        self._execute_club(players, cards, disabled_abilities, damage_modifiers)
        
        # 6. Spade (defense bonus)
        self._execute_spade(players, cards, disabled_abilities, defense_modifiers)
        
        # 7. Diamond (vault manipulation)
        if draw_pile:
            self.execute_diamond_ability(players, cards, disabled_abilities, draw_pile)
        
        # 8. Heart is handled separately after winner determination
        
        result = AbilityResult(
            damage_modifiers=damage_modifiers,
            defense_modifiers=defense_modifiers,
            disabled_abilities=disabled_abilities,
            jack_count=jack_count,
            king_activated=king_activated
        )
        return result
    
    def _execute_queen(self, players: List, cards: List[List], disabled_abilities: Dict[int, List[int]],
                       queen_choices: Dict[int, List[int]] = None) -> Dict[int, List[int]]:
        """Step 1: Queen disables opponent abilities based on vault size.
        Returns a dict of {player_idx: [card_indices]} that Queen disabled."""
        queen_disabled = {}
        for i, player_cards in enumerate(cards):
            opponent_idx = 1 - i
            for card in player_cards:
                if card.rank == 'Q':
                    card_idx = player_cards.index(card)
                    if i in disabled_abilities and card_idx in disabled_abilities[i]:
                        continue

                    player_vault_size = players[i].vault.size()
                    opponent_vault_size = players[opponent_idx].vault.size()
                    disable_count = 2 if player_vault_size < opponent_vault_size else 1

                    if opponent_idx not in disabled_abilities:
                        disabled_abilities[opponent_idx] = []
                    if opponent_idx not in queen_disabled:
                        queen_disabled[opponent_idx] = []

                    if queen_choices and i in queen_choices:
                        chosen = queen_choices[i]
                        for j in chosen[:disable_count]:
                            if j not in disabled_abilities[opponent_idx]:
                                disabled_abilities[opponent_idx].append(j)
                                queen_disabled[opponent_idx].append(j)
                    else:
                        for j in range(min(disable_count, len(cards[opponent_idx]))):
                            if j not in disabled_abilities[opponent_idx]:
                                disabled_abilities[opponent_idx].append(j)
                                queen_disabled[opponent_idx].append(j)
                    break  # Only one Queen ability per player
        return queen_disabled

    def _execute_ace(self, players: List, cards: List[List], disabled_abilities: Dict[int, List[int]],
                     queen_disabled: Dict[int, List[int]] = None) -> None:
        """Step 2: Ace disables J and K abilities. Also undoes Queen's disables
        (re-enables cards that Queen disabled)."""
        ace_played = False
        for i, player_cards in enumerate(cards):
            for card in player_cards:
                if card.rank == 'A':
                    ace_played = True
                    break
            if ace_played:
                break

        if ace_played:
            # Undo Queen's disables — re-enable cards that Queen disabled
            if queen_disabled:
                for player_idx, indices in queen_disabled.items():
                    if player_idx in disabled_abilities:
                        for j in indices:
                            if j in disabled_abilities[player_idx]:
                                disabled_abilities[player_idx].remove(j)

            # Disable J and K abilities
            for i, player_cards in enumerate(cards):
                for j, card in enumerate(player_cards):
                    if card.rank in ['J', 'K']:
                        if i not in disabled_abilities:
                            disabled_abilities[i] = []
                        if j not in disabled_abilities[i]:
                            disabled_abilities[i].append(j)

    def _execute_jack(self, players: List, cards: List[List], disabled_abilities: Dict[int, List[int]]) -> int:
        """Step 3: Count Jacks for reversal logic."""
        jack_count = 0
        for i, player_cards in enumerate(cards):
            for j, card in enumerate(player_cards):
                if i in disabled_abilities and j in disabled_abilities[i]:
                    continue
                if card.rank == 'J':
                    jack_count += 1
        return jack_count

    def _execute_king(self, players: List, cards: List[List], disabled_abilities: Dict[int, List[int]]) -> bool:
        """Step 4: King deals damage equal to opponent vault size + vault reduction. Non-stacking."""
        king_activated = False
        for i, player_cards in enumerate(cards):
            for j, card in enumerate(player_cards):
                if i in disabled_abilities and j in disabled_abilities[i]:
                    continue
                if card.rank == 'K' and not king_activated:
                    opponent_idx = 1 - i
                    opponent = players[opponent_idx]
                    king_damage = opponent.vault.size()
                    vault_reduction = opponent.vault.size() // 4
                    opponent.vault.remove_cards_from_game(vault_reduction)
                    opponent.take_damage(standard_dmg=king_damage, true_dmg=0)
                    king_activated = True
        return king_activated

    def _execute_club(self, players: List, cards: List[List], disabled_abilities: Dict[int, List[int]],
                      damage_modifiers: Dict[int, int]) -> None:
        """Step 5: Club adds damage bonus = floor(vault_size / 2)."""
        for i, player_cards in enumerate(cards):
            for j, card in enumerate(player_cards):
                if i in disabled_abilities and j in disabled_abilities[i]:
                    continue
                if card.is_numbered_card() and card.suit == 'Club':
                    bonus = players[i].vault.size() // 2
                    damage_modifiers[i] += bonus

    def _execute_spade(self, players: List, cards: List[List], disabled_abilities: Dict[int, List[int]],
                       defense_modifiers: Dict[int, int]) -> None:
        """Step 6: Spade adds defense bonus = floor(vault_size / 2)."""
        for i, player_cards in enumerate(cards):
            for j, card in enumerate(player_cards):
                if i in disabled_abilities and j in disabled_abilities[i]:
                    continue
                if card.is_numbered_card() and card.suit == 'Spade':
                    bonus = players[i].vault.size() // 2
                    defense_modifiers[i] += bonus
                    players[i].add_defense(bonus)

    # Keep legacy methods for backward compatibility with tests that call them directly
    def execute_pre_reveal_abilities(self, players: List, cards: List[List], disabled_abilities: Dict[int, List[int]],
                                     queen_choices: Dict[int, List[int]] = None) -> None:
        """Execute Queen then Ace abilities."""
        queen_disabled = self._execute_queen(players, cards, disabled_abilities, queen_choices)
        self._execute_ace(players, cards, disabled_abilities, queen_disabled)

    def execute_post_reveal_abilities(self, players: List, cards: List[List], disabled_abilities: Dict[int, List[int]], 
                                      damage_modifiers: Dict[int, int], defense_modifiers: Dict[int, int]) -> tuple:
        """Execute Jack, King, Club, Spade abilities in order."""
        jack_count = self._execute_jack(players, cards, disabled_abilities)
        king_activated = self._execute_king(players, cards, disabled_abilities)
        self._execute_club(players, cards, disabled_abilities, damage_modifiers)
        self._execute_spade(players, cards, disabled_abilities, defense_modifiers)
        return jack_count, king_activated

    def execute_post_winner_abilities(self, winner, cards: List, disabled_abilities: Dict[int, List[int]], winner_idx: int) -> None:
        """Step 8: Heart heals the round winner."""
        for j, card in enumerate(cards):
            if winner_idx in disabled_abilities and j in disabled_abilities[winner_idx]:
                continue
            if card.is_numbered_card() and card.suit == 'Heart':
                heal_amount = winner.vault.size() // 4
                winner.heal(heal_amount)

    def execute_diamond_ability(self, players: List, cards: List[List], disabled_abilities: Dict[int, List[int]], draw_pile) -> None:
        """
        Execute Diamond ability after score calculation.
        
        Diamond: Remove random card from any vault and shuffle back into draw pile.
        
        Args:
            players: List of both players [player1, player2]
            cards: List of card lists for each player [[cards1], [cards2]]
            disabled_abilities: Dict of disabled abilities {player_id: [card_indices]}
            draw_pile: The game's draw pile (Deck object)
        """
        import random
        
        for i, player_cards in enumerate(cards):
            for j, card in enumerate(player_cards):
                # Skip if this card's ability is disabled
                if i in disabled_abilities and j in disabled_abilities[i]:
                    continue
                
                # Only numbered Diamond cards trigger this ability
                if card.is_numbered_card() and card.suit == 'Diamond':
                    # Collect all non-empty vaults
                    available_vaults = []
                    for idx, player in enumerate(players):
                        if not player.vault.is_empty():
                            available_vaults.append(idx)
                    
                    # If at least one vault has cards, remove a random card
                    if available_vaults:
                        # Choose a random vault
                        vault_idx = random.choice(available_vaults)
                        removed_card = players[vault_idx].vault.remove_random_card()
                        
                        if removed_card:
                            # Add card back to draw pile
                            draw_pile.add_cards([removed_card])
