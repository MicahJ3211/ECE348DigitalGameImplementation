"""Property-based tests for Deck operations.

Feature: card-game-core, Property 5: Deck Shuffling
Feature: card-game-core, Property 47: Draw Order
Feature: card-game-core, Property 48: Draw Pile Tracking
Validates: Requirements 2.4, 24.1, 24.2, 24.3
"""

from hypothesis import given, settings, assume
import hypothesis.strategies as st

from src.entities.card import Card
from src.entities.deck import Deck

ALL_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
ALL_SUITS = ['Club', 'Spade', 'Heart', 'Diamond']

card_strategy = st.builds(
    Card,
    rank=st.sampled_from(ALL_RANKS),
    suit=st.sampled_from(ALL_SUITS),
)


def build_full_deck() -> list:
    """Build a standard 52-card deck."""
    return [Card(rank=r, suit=s) for r in ALL_RANKS for s in ALL_SUITS]


class TestDeckShuffling:
    """**Validates: Requirements 2.4**

    Property 5: Deck Shuffling - For any combined 52-card deck, after shuffling,
    the card order should be randomized (with high probability of being different
    from the original order).
    """

    @settings(max_examples=100)
    @given(data=st.data())
    def test_shuffle_preserves_all_cards(self, data: st.DataObject) -> None:
        """After shuffling, the deck should contain the same cards (same multiset)."""
        cards = build_full_deck()
        original_cards = list(cards)
        deck = Deck(cards)
        deck.shuffle()

        # Draw all cards to inspect the shuffled order
        drawn = deck.draw(52)
        assert len(drawn) == 52

        # Same multiset of cards
        original_reprs = sorted(repr(c) for c in original_cards)
        drawn_reprs = sorted(repr(c) for c in drawn)
        assert original_reprs == drawn_reprs

    @settings(max_examples=100)
    @given(data=st.data())
    def test_shuffle_changes_card_order(self, data: st.DataObject) -> None:
        """After shuffling a 52-card deck, the order should differ from the original
        with very high probability. We allow up to 5 attempts to account for the
        astronomically unlikely case of a shuffle producing the same order."""
        cards = build_full_deck()
        original_order = [repr(c) for c in cards]

        shuffled_differs = False
        for _ in range(5):
            deck = Deck(list(cards))
            deck.shuffle()
            drawn = deck.draw(52)
            shuffled_order = [repr(c) for c in drawn]
            if shuffled_order != original_order:
                shuffled_differs = True
                break

        assert shuffled_differs, "Shuffle did not change card order after 5 attempts"

    @settings(max_examples=100)
    @given(data=st.data())
    def test_shuffle_preserves_deck_size(self, data: st.DataObject) -> None:
        """Shuffling should not change the number of cards in the deck."""
        cards = build_full_deck()
        deck = Deck(cards)
        size_before = deck.remaining()
        deck.shuffle()
        assert deck.remaining() == size_before


class TestDrawOrder:
    """**Validates: Requirements 24.2**

    Property 47: Draw Order - For any draw operation, cards should be drawn
    from the top of the draw pile in order.
    """

    @settings(max_examples=100)
    @given(
        cards=st.lists(card_strategy, min_size=1, max_size=52),
        draw_count=st.integers(min_value=1, max_value=52),
    )
    def test_draw_returns_cards_from_top_in_order(self, cards: list, draw_count: int) -> None:
        """Drawing N cards should return the first N cards from the deck in order."""
        deck = Deck(list(cards))
        actual_draw = min(draw_count, len(cards))
        drawn = deck.draw(draw_count)

        expected = cards[:actual_draw]
        assert len(drawn) == len(expected)
        for i in range(len(drawn)):
            assert repr(drawn[i]) == repr(expected[i])

    @settings(max_examples=100)
    @given(cards=st.lists(card_strategy, min_size=2, max_size=52))
    def test_sequential_draws_maintain_order(self, cards: list) -> None:
        """Drawing cards one at a time should yield the same order as the original list."""
        deck = Deck(list(cards))
        drawn_one_by_one = []
        for _ in range(len(cards)):
            result = deck.draw(1)
            if result:
                drawn_one_by_one.extend(result)

        assert len(drawn_one_by_one) == len(cards)
        for i in range(len(cards)):
            assert repr(drawn_one_by_one[i]) == repr(cards[i])

    @settings(max_examples=100)
    @given(
        cards=st.lists(card_strategy, min_size=3, max_size=52),
        first_draw=st.integers(min_value=1, max_value=10),
    )
    def test_second_draw_continues_from_where_first_left_off(self, cards: list, first_draw: int) -> None:
        """A second draw should start from where the first draw ended."""
        first_draw = min(first_draw, len(cards) - 1)
        assume(first_draw >= 1)

        deck = Deck(list(cards))
        first_batch = deck.draw(first_draw)
        second_batch = deck.draw(1)

        assert len(first_batch) == first_draw
        assert len(second_batch) == 1
        assert repr(second_batch[0]) == repr(cards[first_draw])


class TestDrawPileTracking:
    """**Validates: Requirements 24.3**

    Property 48: Draw Pile Tracking - For any draw pile operations (drawing cards,
    adding tied cards), the remaining card count should accurately reflect the
    number of cards in the pile.
    """

    @settings(max_examples=100)
    @given(cards=st.lists(card_strategy, min_size=0, max_size=52))
    def test_initial_remaining_equals_card_count(self, cards: list) -> None:
        """A new deck's remaining() should equal the number of cards provided."""
        deck = Deck(list(cards))
        assert deck.remaining() == len(cards)

    @settings(max_examples=100)
    @given(
        cards=st.lists(card_strategy, min_size=1, max_size=52),
        draw_count=st.integers(min_value=1, max_value=60),
    )
    def test_remaining_decreases_after_draw(self, cards: list, draw_count: int) -> None:
        """After drawing N cards, remaining should decrease by the actual number drawn."""
        deck = Deck(list(cards))
        initial = deck.remaining()
        drawn = deck.draw(draw_count)
        assert deck.remaining() == initial - len(drawn)

    @settings(max_examples=100)
    @given(
        initial_cards=st.lists(card_strategy, min_size=0, max_size=30),
        added_cards=st.lists(card_strategy, min_size=1, max_size=20),
    )
    def test_remaining_increases_after_add_cards(self, initial_cards: list, added_cards: list) -> None:
        """After adding cards (e.g. tied round cards), remaining should increase accordingly."""
        deck = Deck(list(initial_cards))
        initial_remaining = deck.remaining()
        deck.add_cards(added_cards)
        assert deck.remaining() == initial_remaining + len(added_cards)

    @settings(max_examples=100)
    @given(
        cards=st.lists(card_strategy, min_size=1, max_size=52),
        draw_count=st.integers(min_value=1, max_value=60),
    )
    def test_can_draw_consistent_with_remaining(self, cards: list, draw_count: int) -> None:
        """can_draw(n) should return True iff remaining() >= n."""
        deck = Deck(list(cards))
        assert deck.can_draw(draw_count) == (deck.remaining() >= draw_count)

    @settings(max_examples=100)
    @given(
        cards=st.lists(card_strategy, min_size=3, max_size=30),
        tied_cards=st.lists(card_strategy, min_size=1, max_size=6),
        draw_count=st.integers(min_value=1, max_value=10),
    )
    def test_remaining_tracks_through_draw_and_add_sequence(self, cards: list, tied_cards: list, draw_count: int) -> None:
        """Remaining count should stay accurate through a sequence of draws and adds."""
        deck = Deck(list(cards))
        expected_remaining = len(cards)

        # Draw some cards
        drawn = deck.draw(draw_count)
        expected_remaining -= len(drawn)
        assert deck.remaining() == expected_remaining

        # Add tied round cards back
        deck.add_cards(tied_cards)
        expected_remaining += len(tied_cards)
        assert deck.remaining() == expected_remaining
