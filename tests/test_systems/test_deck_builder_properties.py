"""Property-based tests for DeckBuilder deck construction and initial dealing.

Feature: card-game-core, Property 3: Duplicate Card Prevention
Feature: card-game-core, Property 4: Deck Combination
Feature: card-game-core, Property 6: Initial Hand Dealing
Validates: Requirements 2.2, 2.3, 2.5
"""

from hypothesis import given, settings, assume
import hypothesis.strategies as st

from src.entities.card import Card
from src.entities.deck import Deck
from src.entities.player import Player
from src.entities.vault import Vault
from src.systems.deck_builder import DeckBuilder

ALL_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
ALL_SUITS = ['Club', 'Spade', 'Heart', 'Diamond']

# Full standard 52-card deck
ALL_CARDS = [Card(rank=r, suit=s) for r in ALL_RANKS for s in ALL_SUITS]


def _build_full_52() -> list:
    """Return a fresh list of all 52 unique cards."""
    return [Card(rank=r, suit=s) for r in ALL_RANKS for s in ALL_SUITS]


# Strategy: generate a random permutation of the 52 cards, then split into two
# halves of 26 each.  This guarantees no duplicates and valid selections.
@st.composite
def two_player_selections(draw):
    """Generate two disjoint 26-card selections covering all 52 cards."""
    cards = _build_full_52()
    perm = draw(st.permutations(cards))
    return list(perm[:26]), list(perm[26:])


# Strategy: pick a single card from the full deck
card_strategy = st.sampled_from(ALL_CARDS)


class TestDuplicateCardPrevention:
    """**Validates: Requirements 2.2**

    Property 3: Duplicate Card Prevention
    For any card in the deck, if one player selects it during deck building,
    the other player should not be able to select the same card.
    """

    @given(
        card_rank=st.sampled_from(ALL_RANKS),
        card_suit=st.sampled_from(ALL_SUITS),
    )
    @settings(max_examples=100)
    def test_same_card_rejected_for_second_player(
        self, card_rank: str, card_suit: str
    ) -> None:
        """When player 0 selects a card, player 1 selecting the identical card
        should be rejected (return False)."""
        builder = DeckBuilder()
        card = Card(rank=card_rank, suit=card_suit)

        # Player 0 selects the card successfully
        assert builder.select_card(0, card) is True

        # Player 1 tries the same card — must be rejected
        duplicate = Card(rank=card_rank, suit=card_suit)
        assert builder.select_card(1, duplicate) is False

    @given(
        card_rank=st.sampled_from(ALL_RANKS),
        card_suit=st.sampled_from(ALL_SUITS),
    )
    @settings(max_examples=100)
    def test_same_card_rejected_for_same_player(
        self, card_rank: str, card_suit: str
    ) -> None:
        """A player selecting the same card twice should be rejected."""
        builder = DeckBuilder()
        card = Card(rank=card_rank, suit=card_suit)

        assert builder.select_card(0, card) is True
        duplicate = Card(rank=card_rank, suit=card_suit)
        assert builder.select_card(0, duplicate) is False

    @given(data=st.data())
    @settings(max_examples=100)
    def test_no_card_appears_in_both_selections(self, data) -> None:
        """After filling both players' selections with valid cards, no card
        identifier should appear in both player 0 and player 1 lists."""
        builder = DeckBuilder()
        cards = _build_full_52()
        perm = data.draw(st.permutations(cards))
        p0_cards = list(perm[:26])
        p1_cards = list(perm[26:])

        for c in p0_cards:
            assert builder.select_card(0, c) is True
        for c in p1_cards:
            assert builder.select_card(1, c) is True

        p0_ids = {f"{c.rank}_{c.suit}" for c in builder.player_selections[0]}
        p1_ids = {f"{c.rank}_{c.suit}" for c in builder.player_selections[1]}
        assert p0_ids.isdisjoint(p1_ids), (
            f"Overlap found: {p0_ids & p1_ids}"
        )


class TestDeckCombination:
    """**Validates: Requirements 2.3**

    Property 4: Deck Combination
    For any two valid 26-card selections from different players, combining them
    should produce exactly one 52-card game deck containing all selected cards.
    """

    @given(selections=two_player_selections())
    @settings(max_examples=100)
    def test_combined_deck_has_52_cards(self, selections) -> None:
        """create_game_deck() should return a Deck with exactly 52 cards."""
        p0_cards, p1_cards = selections
        builder = DeckBuilder()

        for c in p0_cards:
            builder.select_card(0, c)
        for c in p1_cards:
            builder.select_card(1, c)

        deck = builder.create_game_deck()
        assert deck.remaining() == 52

    @given(selections=two_player_selections())
    @settings(max_examples=100)
    def test_combined_deck_contains_all_selected_cards(self, selections) -> None:
        """Every card from both selections must appear in the combined deck."""
        p0_cards, p1_cards = selections
        builder = DeckBuilder()

        for c in p0_cards:
            builder.select_card(0, c)
        for c in p1_cards:
            builder.select_card(1, c)

        deck = builder.create_game_deck()

        # Draw all 52 cards and verify they match the union of selections
        drawn = deck.draw(52)
        drawn_ids = sorted(f"{c.rank}_{c.suit}" for c in drawn)
        expected_ids = sorted(
            f"{c.rank}_{c.suit}" for c in p0_cards + p1_cards
        )
        assert drawn_ids == expected_ids, (
            "Combined deck must contain exactly the union of both selections"
        )

    @given(selections=two_player_selections())
    @settings(max_examples=100)
    def test_combined_deck_has_no_duplicates(self, selections) -> None:
        """The combined deck should contain no duplicate cards."""
        p0_cards, p1_cards = selections
        builder = DeckBuilder()

        for c in p0_cards:
            builder.select_card(0, c)
        for c in p1_cards:
            builder.select_card(1, c)

        deck = builder.create_game_deck()
        drawn = deck.draw(52)
        drawn_ids = [f"{c.rank}_{c.suit}" for c in drawn]
        assert len(drawn_ids) == len(set(drawn_ids)), (
            "Combined deck should have no duplicate cards"
        )


class TestInitialHandDealing:
    """**Validates: Requirements 2.5**

    Property 6: Initial Hand Dealing
    For any shuffled deck, dealing initial hands should give each player
    exactly 6 cards and reduce the deck by 12 cards.
    """

    @given(selections=two_player_selections())
    @settings(max_examples=100)
    def test_each_player_gets_six_cards(self, selections) -> None:
        """After deal_initial_hands, each player's hand should have 6 cards."""
        p0_cards, p1_cards = selections
        builder = DeckBuilder()

        for c in p0_cards:
            builder.select_card(0, c)
        for c in p1_cards:
            builder.select_card(1, c)

        deck = builder.create_game_deck()

        p1 = Player(player_id=1, deck=deck)
        p2 = Player(player_id=2, deck=deck)
        players = [p1, p2]

        builder.deal_initial_hands(deck, players)

        assert len(p1.hand) == 6, f"Player 1 should have 6 cards, got {len(p1.hand)}"
        assert len(p2.hand) == 6, f"Player 2 should have 6 cards, got {len(p2.hand)}"

    @given(selections=two_player_selections())
    @settings(max_examples=100)
    def test_deck_reduced_by_twelve(self, selections) -> None:
        """After dealing, the deck should have 52 - 12 = 40 cards remaining."""
        p0_cards, p1_cards = selections
        builder = DeckBuilder()

        for c in p0_cards:
            builder.select_card(0, c)
        for c in p1_cards:
            builder.select_card(1, c)

        deck = builder.create_game_deck()

        p1 = Player(player_id=1, deck=deck)
        p2 = Player(player_id=2, deck=deck)
        players = [p1, p2]

        builder.deal_initial_hands(deck, players)

        assert deck.remaining() == 40, (
            f"Deck should have 40 cards after dealing, got {deck.remaining()}"
        )

    @given(selections=two_player_selections())
    @settings(max_examples=100)
    def test_dealt_cards_are_distinct(self, selections) -> None:
        """Cards dealt to the two players should not overlap."""
        p0_cards, p1_cards = selections
        builder = DeckBuilder()

        for c in p0_cards:
            builder.select_card(0, c)
        for c in p1_cards:
            builder.select_card(1, c)

        deck = builder.create_game_deck()

        p1 = Player(player_id=1, deck=deck)
        p2 = Player(player_id=2, deck=deck)
        players = [p1, p2]

        builder.deal_initial_hands(deck, players)

        p1_ids = {f"{c.rank}_{c.suit}" for c in p1.hand}
        p2_ids = {f"{c.rank}_{c.suit}" for c in p2.hand}
        # Hands should be disjoint (no shared cards)
        assert p1_ids.isdisjoint(p2_ids), (
            f"Dealt hands should not overlap: {p1_ids & p2_ids}"
        )
