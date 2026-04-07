"""AI strategy implementations for the card game.

Four distinct AI personalities:
1. Aggressive Snowball - Clubs & high rank, maximize vault for scaling damage
2. Revolutionary Saboteur - Kings & Diamonds, deplete opponent vault/health
3. Tactical Turtle - Spades & Hearts, defense and healing sustainability
4. Chaos Gambler - Jacks & Aces, reverse logic and disable abilities
"""

import random
from abc import ABC, abstractmethod
from typing import List
from src.entities.card import Card
from src.config import SUITS, RANKS


class AIStrategy(ABC):
    """Base class for AI strategies."""

    name: str = "Base AI"
    description: str = ""

    @abstractmethod
    def choose_cards(self, hand: List[Card], player, opponent) -> List[Card]:
        """Choose 3 cards to play from hand."""

    @abstractmethod
    def build_deck(self, available_cards: List[Card]) -> List[Card]:
        """Choose 26 cards for deck building."""

    @abstractmethod
    def choose_shed(self, player, opponent) -> List[str]:
        """Return list of bonus_type strings for cards to shed. Empty = no shedding."""

    def choose_queen_targets(self, opponent_card_count: int, disable_count: int) -> List[int]:
        """Choose which opponent card indices to disable with Queen. Default: random."""
        indices = list(range(opponent_card_count))
        random.shuffle(indices)
        return indices[:disable_count]



class AggressiveSnowball(AIStrategy):
    """Clubs & high rank cards. Wins rounds early to build vault for Club scaling."""

    name = "Aggressive Snowball"
    description = "Clubs & high cards. Builds vault fast for scaling damage."

    def build_deck(self, available_cards: List[Card]) -> List[Card]:
        # Prioritize: high numbered clubs, then high numbered cards, then face cards
        def score(c):
            suit_bonus = 10 if c.suit == 'Club' else 0
            return c.get_base_damage() + suit_bonus
        ranked = sorted(available_cards, key=score, reverse=True)
        return ranked[:26]

    def choose_cards(self, hand: List[Card], player, opponent) -> List[Card]:
        # Play the 3 highest damage cards
        sorted_hand = sorted(hand, key=lambda c: c.get_base_damage(), reverse=True)
        return sorted_hand[:3]

    def choose_shed(self, player, opponent) -> List[str]:
        # Rarely sheds — wants big vault
        return []


class RevolutionarySaboteur(AIStrategy):
    """Kings & Diamonds. Depletes opponent vault and health over time."""

    name = "Revolutionary Saboteur"
    description = "Kings & Diamonds. Destroys opponent vault and deals heavy damage."

    def build_deck(self, available_cards: List[Card]) -> List[Card]:
        # Prioritize Kings, Diamonds, then high cards
        def score(c):
            if c.rank == 'K':
                return 100
            if c.suit == 'Diamond' and c.is_numbered_card():
                return 50 + c.get_base_damage()
            return c.get_base_damage()
        ranked = sorted(available_cards, key=score, reverse=True)
        return ranked[:26]

    def choose_cards(self, hand: List[Card], player, opponent) -> List[Card]:
        # Save Kings for when opponent has large vault
        kings = [c for c in hand if c.rank == 'K']
        diamonds = [c for c in hand if c.is_numbered_card() and c.suit == 'Diamond']
        others = [c for c in hand if c not in kings and c not in diamonds]

        chosen = []
        # Play King if opponent vault >= 6
        if kings and opponent.vault.size() >= 6:
            chosen.append(kings[0])
        # Fill with diamonds
        for c in diamonds:
            if len(chosen) >= 3:
                break
            if c not in chosen:
                chosen.append(c)
        # Fill with highest remaining
        remaining = sorted([c for c in hand if c not in chosen],
                           key=lambda c: c.get_base_damage(), reverse=True)
        for c in remaining:
            if len(chosen) >= 3:
                break
            chosen.append(c)
        return chosen[:3]

    def choose_shed(self, player, opponent) -> List[str]:
        # Shed for health if below 20
        if player.health < 20 and player.vault.size() > 0:
            return ['health']
        return []


class TacticalTurtle(AIStrategy):
    """Spades & Hearts. Builds defense and heals to outlast opponent."""

    name = "Tactical Turtle"
    description = "Spades & Hearts. Builds defense wall and heals to outlast."

    def build_deck(self, available_cards: List[Card]) -> List[Card]:
        # Prioritize Spades, Hearts, then high cards
        def score(c):
            if c.suit == 'Spade' and c.is_numbered_card():
                return 60 + c.get_base_damage()
            if c.suit == 'Heart' and c.is_numbered_card():
                return 50 + c.get_base_damage()
            return c.get_base_damage()
        ranked = sorted(available_cards, key=score, reverse=True)
        return ranked[:26]

    def choose_cards(self, hand: List[Card], player, opponent) -> List[Card]:
        # Prioritize Spades for defense, then Hearts for healing, then highest damage
        spades = [c for c in hand if c.is_numbered_card() and c.suit == 'Spade']
        hearts = [c for c in hand if c.is_numbered_card() and c.suit == 'Heart']
        others = sorted([c for c in hand if c not in spades and c not in hearts],
                        key=lambda c: c.get_base_damage(), reverse=True)

        chosen = []
        for c in spades:
            if len(chosen) >= 3:
                break
            chosen.append(c)
        for c in hearts:
            if len(chosen) >= 3:
                break
            chosen.append(c)
        for c in others:
            if len(chosen) >= 3:
                break
            chosen.append(c)
        return chosen[:3]

    def choose_shed(self, player, opponent) -> List[str]:
        # Shed for defense frequently
        sheds = []
        if player.vault.size() > 4:
            sheds.append('defense')
        return sheds


class ChaosGambler(AIStrategy):
    """Jacks & Aces. Reverses logic and disables face abilities."""

    name = "Chaos Gambler"
    description = "Jacks & Aces. Flips round logic and disables opponent abilities."

    def build_deck(self, available_cards: List[Card]) -> List[Card]:
        # Prioritize Jacks, Aces, then low numbered cards
        def score(c):
            if c.rank == 'J':
                return 100
            if c.rank == 'A':
                return 90
            if c.is_numbered_card():
                return 30 - c.get_base_damage()  # prefer low cards
            return 10
        ranked = sorted(available_cards, key=score, reverse=True)
        return ranked[:26]

    def choose_cards(self, hand: List[Card], player, opponent) -> List[Card]:
        # Play Jack + lowest cards to win via reversal
        jacks = [c for c in hand if c.rank == 'J']
        aces = [c for c in hand if c.rank == 'A']
        low_cards = sorted([c for c in hand if c not in jacks and c not in aces],
                           key=lambda c: c.get_base_damage())

        chosen = []
        # Play exactly 1 Jack (odd count = reversal)
        if jacks:
            chosen.append(jacks[0])
        # Play Ace to disable opponent face cards
        for c in aces:
            if len(chosen) >= 3:
                break
            chosen.append(c)
        # Fill with lowest cards
        for c in low_cards:
            if len(chosen) >= 3:
                break
            chosen.append(c)
        # If still not enough, fill from hand
        for c in hand:
            if len(chosen) >= 3:
                break
            if c not in chosen:
                chosen.append(c)
        return chosen[:3]

    def choose_shed(self, player, opponent) -> List[str]:
        # Occasionally shed for damage
        if player.vault.size() > 6:
            return ['damage']
        return []


ALL_STRATEGIES = [
    AggressiveSnowball(),
    RevolutionarySaboteur(),
    TacticalTurtle(),
    ChaosGambler(),
]
