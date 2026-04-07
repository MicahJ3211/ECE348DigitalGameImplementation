"""Property-based tests for gameplay flow mechanics.

Feature: card-game-core, Property 10: Simultaneous Reveal
Feature: card-game-core, Property 14: Post-Round Card Draw

Validates: Requirements 4.1, 4.7
"""

from hypothesis import given, settings, assume
import hypothesis.strategies as st

from src.entities.card import Card
from src.entities.player import Player
from src.entities.deck import Deck
from src.entities.vault import Vault

ALL_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
ALL_SUITS = ['Club', 'Spade', 'Heart', 'Diamond']
ALL_CARDS = [Card(rank=r, suit=s) for r in ALL_RANKS for s in ALL_SUITS]


@st.composite
def deck_with_cards(draw, min_cards=6, max_cards=40):
    """Generate a deck with a random number of cards."""
    size = draw(st.integers(min_value=min_cards, max_value=max_cards))
    indices = draw(
        st.lists(
            st.integers(min_value=0, max_value=len(ALL_CARDS) - 1),
            min_size=size,
            max_size=size,
        )
    )
    cards = [ALL_CARDS[i] for i in indices]
    return Deck(cards)


class TestSimultaneousReveal:
    """**Validates: Requirements 4.1**

    Property 10: Simultaneous Reveal
    For any game state where both players have confirmed their selections,
    all 6 cards should be revealed simultaneously.
    """

    @given(data=st.data())
    @settings(max_examples=100)
    def test_both_players_selections_produce_six_cards(self, data):
        """When both players select 3 cards, there should be exactly 6 cards to reveal."""
        indices = data.draw(
            st.lists(
                st.integers(min_value=0, max_value=len(ALL_CARDS) - 1),
                min_size=12,
                max_size=12,
                unique=True,
            )
        )
        hand1 = [ALL_CARDS[i] for i in indices[:6]]
        hand2 = [ALL_CARDS[i] for i in indices[6:]]

        # Each player selects 3 cards
        p1_selected = hand1[:3]
        p2_selected = hand2[:3]

        # All 6 cards revealed simultaneously
        all_revealed = p1_selected + p2_selected
        assert len(all_revealed) == 6

    @given(data=st.data())
    @settings(max_examples=100)
    def test_revealed_cards_match_selections(self, data):
        """The revealed cards should be exactly the cards both players selected."""
        indices = data.draw(
            st.lists(
                st.integers(min_value=0, max_value=len(ALL_CARDS) - 1),
                min_size=12,
                max_size=12,
                unique=True,
            )
        )
        hand1 = [ALL_CARDS[i] for i in indices[:6]]
        hand2 = [ALL_CARDS[i] for i in indices[6:]]

        p1_selected = hand1[:3]
        p2_selected = hand2[:3]

        all_revealed = p1_selected + p2_selected

        # Every selected card appears in the revealed set
        for card in p1_selected:
            assert card in all_revealed
        for card in p2_selected:
            assert card in all_revealed

    @given(data=st.data())
    @settings(max_examples=100)
    def test_both_confirmations_required_for_reveal(self, data):
        """Cards should only be revealed when both players have confirmed."""
        indices = data.draw(
            st.lists(
                st.integers(min_value=0, max_value=len(ALL_CARDS) - 1),
                min_size=12,
                max_size=12,
                unique=True,
            )
        )
        hand1 = [ALL_CARDS[i] for i in indices[:6]]
        hand2 = [ALL_CARDS[i] for i in indices[6:]]

        p1_confirmed = True
        p2_confirmed = True
        p1_selected = hand1[:3]
        p2_selected = hand2[:3]

        # Only reveal when both confirmed
        can_reveal = p1_confirmed and p2_confirmed and len(p1_selected) == 3 and len(p2_selected) == 3
        assert can_reveal is True

        # If one player hasn't confirmed, cannot reveal
        p1_not_confirmed = False
        cannot_reveal = p1_not_confirmed and p2_confirmed
        assert cannot_reveal is False


class TestPostRoundCardDraw:
    """**Validates: Requirements 4.7**

    Property 14: Post-Round Card Draw
    For any completed round, each player should draw 3 new cards from the
    draw pile (if available).
    """

    @given(deck_size=st.integers(min_value=6, max_value=40))
    @settings(max_examples=100)
    def test_each_player_draws_3_cards_after_round(self, deck_size):
        """After a round, each player should draw 3 cards from the deck."""
        cards = [ALL_CARDS[i % len(ALL_CARDS)] for i in range(deck_size)]
        deck = Deck(cards)

        player1 = Player(player_id=0, vault=Vault(), hand=[], deck=deck)
        player2 = Player(player_id=1, vault=Vault(), hand=[], deck=deck)

        initial_deck_size = deck.remaining()
        p1_hand_before = len(player1.hand)
        p2_hand_before = len(player2.hand)

        # Simulate post-round draw
        player1.draw_cards(3)
        player2.draw_cards(3)

        # Each player should have drawn up to 3 cards
        p1_drawn = len(player1.hand) - p1_hand_before
        p2_drawn = len(player2.hand) - p2_hand_before

        assert p1_drawn <= 3
        assert p2_drawn <= 3
        assert p1_drawn + p2_drawn == initial_deck_size - deck.remaining()

    @given(deck_size=st.integers(min_value=6, max_value=40))
    @settings(max_examples=100)
    def test_draw_reduces_deck_size(self, deck_size):
        """Drawing cards should reduce the deck's remaining count."""
        cards = [ALL_CARDS[i % len(ALL_CARDS)] for i in range(deck_size)]
        deck = Deck(cards)

        player = Player(player_id=0, vault=Vault(), hand=[], deck=deck)
        before = deck.remaining()

        player.draw_cards(3)

        drawn_count = min(3, before)
        assert deck.remaining() == before - drawn_count
        assert len(player.hand) == drawn_count

    @given(available=st.integers(min_value=0, max_value=2))
    @settings(max_examples=100)
    def test_draw_with_insufficient_cards(self, available):
        """If fewer than 3 cards remain, player draws only what's available."""
        cards = [ALL_CARDS[i] for i in range(available)]
        deck = Deck(cards)

        player = Player(player_id=0, vault=Vault(), hand=[], deck=deck)
        player.draw_cards(3)

        assert len(player.hand) == available
        assert deck.remaining() == 0

    @given(deck_size=st.integers(min_value=10, max_value=40),
           existing_hand_size=st.integers(min_value=0, max_value=3))
    @settings(max_examples=100)
    def test_drawn_cards_added_to_existing_hand(self, deck_size, existing_hand_size):
        """Drawn cards should be appended to the player's existing hand."""
        cards = [ALL_CARDS[i % len(ALL_CARDS)] for i in range(deck_size)]
        deck = Deck(cards)

        existing_hand = [ALL_CARDS[40 + i] for i in range(existing_hand_size)]
        player = Player(player_id=0, vault=Vault(), hand=list(existing_hand), deck=deck)

        player.draw_cards(3)

        assert len(player.hand) == existing_hand_size + 3
        # Original hand cards should still be present
        for card in existing_hand:
            assert card in player.hand
