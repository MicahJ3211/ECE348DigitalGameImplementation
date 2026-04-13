"""Headless AI vs AI game simulator.

Runs complete games without pygame rendering for fast batch simulation.
"""

import random
from typing import List, Dict, Tuple
from src.entities.card import Card
from src.entities.player import Player
from src.entities.vault import Vault
from src.entities.deck import Deck
from src.systems.combat_system import CombatSystem
from src.systems.ability_resolver import AbilityResolver
from src.systems.ai_strategies import AIStrategy
from src.config import SUITS, RANKS, STARTING_HAND_SIZE


def _make_full_deck() -> List[Card]:
    return [Card(rank=r, suit=s) for s in SUITS for r in RANKS]


class SimulationResult:
    """Result of a single simulated game."""

    def __init__(self, winner_id: int, reason: str, rounds: int,
                 p1_health: int, p2_health: int, p1_vault: int, p2_vault: int,
                 p1_deck: List[Card] = None, p2_deck: List[Card] = None):
        self.winner_id = winner_id  # 1 or 2, None for tie
        self.reason = reason
        self.rounds = rounds
        self.p1_health = p1_health
        self.p2_health = p2_health
        self.p1_vault = p1_vault
        self.p2_vault = p2_vault
        self.p1_deck = p1_deck or []
        self.p2_deck = p2_deck or []


class BatchResult:
    """Aggregated results from multiple simulated games."""

    def __init__(self, ai1_name: str, ai2_name: str):
        self.ai1_name = ai1_name
        self.ai2_name = ai2_name
        self.games: List[SimulationResult] = []

    def add(self, result: SimulationResult):
        self.games.append(result)

    @property
    def total(self) -> int:
        return len(self.games)

    @property
    def ai1_wins(self) -> int:
        return sum(1 for g in self.games if g.winner_id == 1)

    @property
    def ai2_wins(self) -> int:
        return sum(1 for g in self.games if g.winner_id == 2)

    @property
    def ties(self) -> int:
        return sum(1 for g in self.games if g.winner_id is None)

    @property
    def avg_rounds(self) -> float:
        return sum(g.rounds for g in self.games) / max(1, len(self.games))

    @property
    def avg_vault_diff(self) -> float:
        """Average absolute difference between P1 and P2 vault sizes."""
        return sum(abs(g.p1_vault - g.p2_vault) for g in self.games) / max(1, len(self.games))


def simulate_game(ai1: AIStrategy, ai2: AIStrategy, max_rounds: int = 100) -> SimulationResult:
    """Run a single headless game between two AIs."""
    combat = CombatSystem()
    resolver = AbilityResolver(combat)

    # Deck building phase
    all_cards = _make_full_deck()
    ai1_deck_cards = ai1.build_deck(list(all_cards))
    # Give remaining cards to ai2
    ai1_ids = {f"{c.rank}_{c.suit}" for c in ai1_deck_cards}
    ai2_pool = [c for c in all_cards if f"{c.rank}_{c.suit}" not in ai1_ids]
    ai2_deck_cards = ai2.build_deck(ai2_pool)

    # Combine and shuffle
    combined = ai1_deck_cards + ai2_deck_cards
    deck = Deck(combined)
    deck.shuffle()

    # Save deck snapshots for results
    p1_deck_snapshot = list(ai1_deck_cards)
    p2_deck_snapshot = list(ai2_deck_cards)

    # Create players
    p1 = Player(player_id=1, vault=Vault())
    p2 = Player(player_id=2, vault=Vault())
    p1.deck = deck
    p2.deck = deck
    p1.hand = deck.draw(STARTING_HAND_SIZE)
    p2.hand = deck.draw(STARTING_HAND_SIZE)

    round_num = 0
    while round_num < max_rounds:
        round_num += 1

        # Check if both can play
        if len(p1.hand) < 3 and not deck.can_draw(3 - len(p1.hand)):
            break
        if len(p2.hand) < 3 and not deck.can_draw(3 - len(p2.hand)):
            break

        # Defense decay
        p1.decay_defense()
        p2.decay_defense()

        # Shedding
        for bonus in ai1.choose_shed(p1, p2):
            p1.shed_card(bonus)
            if bonus == 'health':
                p1.heal(1)
            elif bonus == 'defense':
                p1.add_defense(1)
        for bonus in ai2.choose_shed(p2, p1):
            p2.shed_card(bonus)
            if bonus == 'health':
                p2.heal(1)
            elif bonus == 'defense':
                p2.add_defense(1)

        # Card selection
        if len(p1.hand) < 3:
            p1.draw_cards(3 - len(p1.hand))
        if len(p2.hand) < 3:
            p2.draw_cards(3 - len(p2.hand))

        cards1 = ai1.choose_cards(p1.hand, p1, p2)
        cards2 = ai2.choose_cards(p2.hand, p2, p1)

        # Ensure exactly 3 cards (fallback)
        cards1 = cards1[:3]
        cards2 = cards2[:3]
        if len(cards1) < 3 or len(cards2) < 3:
            break

        for c in cards1:
            if c in p1.hand:
                p1.hand.remove(c)
        for c in cards2:
            if c in p2.hand:
                p2.hand.remove(c)

        # Queen choices (AI auto-picks)
        queen_choices = {}
        for i, (ai, cards, opp) in enumerate([(ai1, cards1, p2), (ai2, cards2, p1)]):
            has_queen = any(c.rank == 'Q' for c in cards)
            if has_queen:
                opp_cards = cards2 if i == 0 else cards1
                vault_self = p1.vault.size() if i == 0 else p2.vault.size()
                vault_opp = p2.vault.size() if i == 0 else p1.vault.size()
                count = 2 if vault_self < vault_opp else 1
                count = min(count, len(opp_cards))
                queen_choices[i] = ai.choose_queen_targets(len(opp_cards), count)

        # Resolve abilities
        ability_result = resolver.resolve_abilities(
            p1, p2, cards1, cards2, deck,
            queen_choices=queen_choices if queen_choices else None
        )

        # Calculate damage
        p1_dmg = combat.calculate_base_damage(cards1) + ability_result.damage_modifiers.get(0, 0)
        p2_dmg = combat.calculate_base_damage(cards2) + ability_result.damage_modifiers.get(1, 0)

        winner_id = combat.determine_winner(p1_dmg, p2_dmg, ability_result.jack_count)
        net_damage = abs(p1_dmg - p2_dmg)

        if winner_id == 1:
            combat.apply_damage(p2, net_damage, 0)
            combat.add_to_vault(p1, cards1 + cards2)
            # Heart healing
            for c in cards1:
                if c.is_numbered_card() and c.suit == 'Heart':
                    p1.heal(p1.vault.size() // 4)
                    break
        elif winner_id == 2:
            combat.apply_damage(p1, net_damage, 0)
            combat.add_to_vault(p2, cards1 + cards2)
            for c in cards2:
                if c.is_numbered_card() and c.suit == 'Heart':
                    p2.heal(p2.vault.size() // 4)
                    break
        else:
            deck.add_cards(cards1 + cards2)
            deck.shuffle()

        # Draw new cards
        p1.draw_cards(3)
        p2.draw_cards(3)

        # Check win condition
        win = combat.check_win_condition(p1, p2)
        if win.game_over:
            return SimulationResult(
                winner_id=win.winner_id, reason=win.reason, rounds=round_num,
                p1_health=p1.health, p2_health=p2.health,
                p1_vault=p1.vault.size(), p2_vault=p2.vault.size(),
                p1_deck=p1_deck_snapshot, p2_deck=p2_deck_snapshot
            )

    # Game ended by round limit or insufficient cards — vault-based winner
    if p1.vault.size() > p2.vault.size():
        w = 1
    elif p2.vault.size() > p1.vault.size():
        w = 2
    else:
        w = None
    return SimulationResult(
        winner_id=w, reason='vault', rounds=round_num,
        p1_health=p1.health, p2_health=p2.health,
        p1_vault=p1.vault.size(), p2_vault=p2.vault.size(),
        p1_deck=p1_deck_snapshot, p2_deck=p2_deck_snapshot
    )


def run_batch(ai1: AIStrategy, ai2: AIStrategy, num_games: int = 40) -> BatchResult:
    """Run multiple games and return aggregated results."""
    batch = BatchResult(ai1.name, ai2.name)
    for _ in range(num_games):
        result = simulate_game(ai1, ai2)
        batch.add(result)
    return batch
