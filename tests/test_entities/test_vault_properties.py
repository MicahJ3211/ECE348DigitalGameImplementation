"""Property-based tests for Vault size tracking.

Feature: card-game-core, Property 37: Vault Size Tracking
Validates: Requirements 18.2
"""

from hypothesis import given, settings
import hypothesis.strategies as st

from src.entities.card import Card
from src.entities.vault import Vault

ALL_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
ALL_SUITS = ['Club', 'Spade', 'Heart', 'Diamond']

card_strategy = st.builds(
    Card,
    rank=st.sampled_from(ALL_RANKS),
    suit=st.sampled_from(ALL_SUITS),
)

card_list_strategy = st.lists(card_strategy, min_size=0, max_size=20)


class TestVaultSizeTracking:
    """**Validates: Requirements 18.2**"""

    @given(cards=card_list_strategy)
    @settings(max_examples=100)
    def test_size_after_adding_cards(self, cards: list) -> None:
        """After adding N cards to an empty vault, size should be N."""
        vault = Vault()
        vault.add_cards(cards)
        assert vault.size() == len(cards)

    @given(
        initial_cards=st.lists(card_strategy, min_size=1, max_size=20),
        extra_cards=st.lists(card_strategy, min_size=0, max_size=10),
    )
    @settings(max_examples=100)
    def test_size_after_multiple_adds(self, initial_cards: list, extra_cards: list) -> None:
        """Adding cards in multiple batches should accumulate correctly."""
        vault = Vault()
        vault.add_cards(initial_cards)
        vault.add_cards(extra_cards)
        assert vault.size() == len(initial_cards) + len(extra_cards)

    @given(cards=st.lists(card_strategy, min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_size_after_remove_random_card(self, cards: list) -> None:
        """Removing a random card should decrease vault size by 1."""
        vault = Vault()
        vault.add_cards(cards)
        size_before = vault.size()
        removed = vault.remove_random_card()
        assert removed is not None
        assert vault.size() == size_before - 1

    @given(
        cards=st.lists(card_strategy, min_size=1, max_size=20),
        count=st.integers(min_value=0, max_value=25),
    )
    @settings(max_examples=100)
    def test_size_after_remove_cards_from_game(self, cards: list, count: int) -> None:
        """After removing count cards from game, size should decrease by min(count, original size)."""
        vault = Vault()
        vault.add_cards(cards)
        original_size = vault.size()
        removed = vault.remove_cards_from_game(count)
        expected_removed = min(count, original_size)
        assert len(removed) == expected_removed
        assert vault.size() == original_size - expected_removed

    @given(cards=card_list_strategy)
    @settings(max_examples=100)
    def test_is_empty_consistent_with_size(self, cards: list) -> None:
        """is_empty() should return True iff size() == 0."""
        vault = Vault()
        vault.add_cards(cards)
        assert vault.is_empty() == (vault.size() == 0)

    @settings(max_examples=100)
    @given(
        cards=st.lists(card_strategy, min_size=1, max_size=15),
        num_removals=st.integers(min_value=1, max_value=15),
    )
    def test_size_tracks_through_mixed_operations(self, cards: list, num_removals: int) -> None:
        """Vault size should accurately track through a sequence of adds and removes."""
        vault = Vault()
        vault.add_cards(cards)
        expected_size = len(cards)

        actual_removals = min(num_removals, expected_size)
        for _ in range(actual_removals):
            removed = vault.remove_random_card()
            if removed is not None:
                expected_size -= 1

        assert vault.size() == expected_size
