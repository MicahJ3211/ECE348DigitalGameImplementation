"""Property-based tests for Card entity base damage calculation.

Feature: card-game-core, Property 1: Base Damage Calculation
Validates: Requirements 5.1, 5.2, 5.3
"""

from hypothesis import given, settings
import hypothesis.strategies as st

from src.entities.card import Card

ALL_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
ALL_SUITS = ['Club', 'Spade', 'Heart', 'Diamond']
NUMBERED_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
FACE_RANKS = ['J', 'Q', 'K']


class TestBaseDamageCalculation:
    """**Validates: Requirements 5.1, 5.2, 5.3**"""

    @given(
        suit=st.sampled_from(ALL_SUITS),
    )
    @settings(max_examples=100)
    def test_ace_base_damage_is_one(self, suit: str) -> None:
        """Ace cards should always have base damage of 1, regardless of suit."""
        card = Card(rank='A', suit=suit)
        assert card.get_base_damage() == 1

    @given(
        rank=st.sampled_from(NUMBERED_RANKS),
        suit=st.sampled_from(ALL_SUITS),
    )
    @settings(max_examples=100)
    def test_numbered_card_base_damage_equals_rank(self, rank: str, suit: str) -> None:
        """Numbered cards (2-10) should have base damage equal to their rank value."""
        card = Card(rank=rank, suit=suit)
        assert card.get_base_damage() == int(rank)

    @given(
        rank=st.sampled_from(FACE_RANKS),
        suit=st.sampled_from(ALL_SUITS),
    )
    @settings(max_examples=100)
    def test_face_card_base_damage_is_ten(self, rank: str, suit: str) -> None:
        """Face cards (J, Q, K) should always have base damage of 10."""
        card = Card(rank=rank, suit=suit)
        assert card.get_base_damage() == 10

    @given(
        rank=st.sampled_from(ALL_RANKS),
        suit=st.sampled_from(ALL_SUITS),
    )
    @settings(max_examples=100)
    def test_base_damage_is_always_positive(self, rank: str, suit: str) -> None:
        """For any valid card, base damage should always be a positive integer."""
        card = Card(rank=rank, suit=suit)
        damage = card.get_base_damage()
        assert isinstance(damage, int)
        assert damage >= 1
        assert damage <= 10
