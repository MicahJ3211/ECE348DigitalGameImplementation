"""Property-based tests for InputHandler card selection and input validation.

Feature: card-game-core, Property 7: Card Selection Limit
Feature: card-game-core, Property 8: Selection Reversibility
Feature: card-game-core, Property 43: Hand Validation
Feature: card-game-core, Property 9: Selection Lock After Confirmation
Feature: card-game-core, Property 44: Turn-Based Input Blocking
Validates: Requirements 3.1, 3.3, 3.6, 22.1, 22.2, 22.3, 22.4, 22.5
"""

from hypothesis import given, settings, assume
import hypothesis.strategies as st

from src.entities.card import Card
from src.systems.input_handler import InputHandler

ALL_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
ALL_SUITS = ['Club', 'Spade', 'Heart', 'Diamond']
ALL_CARDS = [Card(rank=r, suit=s) for r in ALL_RANKS for s in ALL_SUITS]


@st.composite
def unique_hand(draw, min_size=4, max_size=6):
    """Generate a hand of unique cards by sampling distinct indices."""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    indices = draw(
        st.lists(
            st.integers(min_value=0, max_value=len(ALL_CARDS) - 1),
            min_size=size,
            max_size=size,
            unique=True,
        )
    )
    return [ALL_CARDS[i] for i in indices]


@st.composite
def hand_of_six(draw):
    """Generate a hand of exactly 6 unique cards."""
    indices = draw(
        st.lists(
            st.integers(min_value=0, max_value=len(ALL_CARDS) - 1),
            min_size=6,
            max_size=6,
            unique=True,
        )
    )
    return [ALL_CARDS[i] for i in indices]


class TestCardSelectionLimit:
    """**Validates: Requirements 3.1, 22.1, 22.3**

    Property 7: Card Selection Limit
    For any player hand, attempting to select more than 3 cards should be
    prevented, and only selections of exactly 3 cards should allow confirmation.
    """

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_selection_of_exactly_3_is_valid(self, hand: list) -> None:
        """Selecting exactly 3 cards from the hand should be a valid selection."""
        handler = InputHandler()
        selected = hand[:3]
        assert handler.is_valid_selection(selected, hand) is True

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_selection_of_fewer_than_3_is_invalid(self, hand: list) -> None:
        """Selecting fewer than 3 cards should not allow confirmation."""
        handler = InputHandler()
        for count in range(min(3, len(hand))):
            selected = hand[:count]
            assert handler.is_valid_selection(selected, hand) is False, (
                f"Selection of {count} cards should be invalid"
            )

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_selection_of_more_than_3_is_invalid(self, hand: list) -> None:
        """Selecting more than 3 cards should not allow confirmation."""
        handler = InputHandler()
        assume(len(hand) > 3)
        selected = hand[:4]
        assert handler.is_valid_selection(selected, hand) is False, (
            "Selection of 4+ cards should be invalid"
        )

    @given(hand=hand_of_six(), num_selected=st.integers(min_value=0, max_value=6))
    @settings(max_examples=100)
    def test_only_exactly_3_allows_confirmation(
        self, hand: list, num_selected: int
    ) -> None:
        """For any number of selected cards, only exactly 3 should be valid."""
        handler = InputHandler()
        selected = hand[:num_selected]
        result = handler.is_valid_selection(selected, hand)
        if num_selected == 3:
            assert result is True, "Exactly 3 cards should be valid"
        else:
            assert result is False, (
                f"Selection of {num_selected} cards should be invalid"
            )


class TestSelectionReversibility:
    """**Validates: Requirements 3.3**

    Property 8: Selection Reversibility
    For any selected card before confirmation, clicking it again should
    deselect it and remove it from the selection.
    """

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_adding_and_removing_card_restores_empty(self, hand: list) -> None:
        """Selecting a card then deselecting it should leave an empty selection."""
        handler = InputHandler()
        card = hand[0]

        handler.selected_cards.append(card)
        assert card in handler.selected_cards

        handler.selected_cards.remove(card)
        assert card not in handler.selected_cards
        assert len(handler.selected_cards) == 0

    @given(hand=unique_hand(min_size=5, max_size=6), deselect_index=st.integers(min_value=0, max_value=2))
    @settings(max_examples=100)
    def test_deselect_removes_specific_card(
        self, hand: list, deselect_index: int
    ) -> None:
        """Deselecting a specific card should remove only that card."""
        handler = InputHandler()
        selected_three = hand[:3]

        for c in selected_three:
            handler.selected_cards.append(c)
        assert len(handler.selected_cards) == 3

        card_to_remove = selected_three[deselect_index]
        handler.selected_cards.remove(card_to_remove)

        assert card_to_remove not in handler.selected_cards
        assert len(handler.selected_cards) == 2
        for i, c in enumerate(selected_three):
            if i != deselect_index:
                assert c in handler.selected_cards

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_select_deselect_reselect_works(self, hand: list) -> None:
        """A card can be selected, deselected, and re-selected."""
        handler = InputHandler()
        card = hand[0]

        handler.selected_cards.append(card)
        assert card in handler.selected_cards

        handler.selected_cards.remove(card)
        assert card not in handler.selected_cards

        handler.selected_cards.append(card)
        assert card in handler.selected_cards
        assert len(handler.selected_cards) == 1


class TestHandValidation:
    """**Validates: Requirements 22.2**

    Property 43: Hand Validation
    For any card selection attempt, only cards currently in the player's
    hand should be selectable.
    """

    @given(hand=hand_of_six(), data=st.data())
    @settings(max_examples=100)
    def test_cards_not_in_hand_make_selection_invalid(
        self, hand: list, data
    ) -> None:
        """Selecting a card not in the hand should make the selection invalid."""
        handler = InputHandler()
        hand_set = {(c.rank, c.suit) for c in hand}
        cards_not_in_hand = [c for c in ALL_CARDS if (c.rank, c.suit) not in hand_set]
        assume(len(cards_not_in_hand) > 0)
        outsider = data.draw(st.sampled_from(cards_not_in_hand))

        selected = hand[:2] + [outsider]
        assert handler.is_valid_selection(selected, hand) is False

    @given(hand=hand_of_six())
    @settings(max_examples=100)
    def test_all_cards_from_hand_is_valid(self, hand: list) -> None:
        """Selecting exactly 3 cards all from the hand should be valid."""
        handler = InputHandler()
        selected = hand[:3]
        assert handler.is_valid_selection(selected, hand) is True

    @given(hand=hand_of_six(), data=st.data())
    @settings(max_examples=100)
    def test_entirely_outside_cards_are_invalid(self, hand: list, data) -> None:
        """Selecting 3 cards none of which are in the hand should be invalid."""
        hand_set = {(c.rank, c.suit) for c in hand}
        cards_not_in_hand = [c for c in ALL_CARDS if (c.rank, c.suit) not in hand_set]
        assume(len(cards_not_in_hand) >= 3)

        indices = data.draw(
            st.lists(
                st.integers(min_value=0, max_value=len(cards_not_in_hand) - 1),
                min_size=3,
                max_size=3,
                unique=True,
            )
        )
        outsiders = [cards_not_in_hand[i] for i in indices]
        handler = InputHandler()
        assert handler.is_valid_selection(outsiders, hand) is False



class TestSelectionLockAfterConfirmation:
    """**Validates: Requirements 3.6**

    Property 9: Selection Lock After Confirmation
    For any confirmed card selection, attempts to modify the selection should
    be rejected until the round completes.
    """

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_lock_prevents_modification(self, hand: list) -> None:
        """After locking, selection_locked should be True."""
        handler = InputHandler()
        handler.selected_cards = hand[:3]
        handler.lock_selection()

        assert handler.selection_locked is True

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_unlock_after_round_allows_modification(self, hand: list) -> None:
        """After unlocking, selection_locked should be False."""
        handler = InputHandler()
        handler.selected_cards = hand[:3]
        handler.lock_selection()
        assert handler.selection_locked is True

        handler.unlock_selection()
        assert handler.selection_locked is False

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_reset_clears_lock(self, hand: list) -> None:
        """Resetting the handler should clear the selection lock."""
        handler = InputHandler()
        handler.selected_cards = hand[:3]
        handler.lock_selection()
        assert handler.selection_locked is True

        handler.reset()
        assert handler.selection_locked is False
        assert len(handler.selected_cards) == 0

    @given(hand=hand_of_six())
    @settings(max_examples=100)
    def test_lock_preserves_selected_cards(self, hand: list) -> None:
        """Locking should not alter the selected cards list."""
        handler = InputHandler()
        selected = hand[:3]
        handler.selected_cards = list(selected)
        handler.lock_selection()

        assert handler.selected_cards == selected
        assert handler.selection_locked is True


class TestTurnBasedInputBlocking:
    """**Validates: Requirements 22.4, 22.5**

    Property 44: Turn-Based Input Blocking
    For any game state during opponent's turn or during ability resolution
    animations, player input should be disabled.
    """

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_block_input_sets_flag(self, hand: list) -> None:
        """Blocking input should set input_blocked to True."""
        handler = InputHandler()
        handler.block_input()
        assert handler.input_blocked is True

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_unblock_input_clears_flag(self, hand: list) -> None:
        """Unblocking input should set input_blocked to False."""
        handler = InputHandler()
        handler.block_input()
        assert handler.input_blocked is True

        handler.unblock_input()
        assert handler.input_blocked is False

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_reset_clears_input_block(self, hand: list) -> None:
        """Resetting the handler should clear the input block."""
        handler = InputHandler()
        handler.block_input()
        assert handler.input_blocked is True

        handler.reset()
        assert handler.input_blocked is False

    @given(hand=unique_hand())
    @settings(max_examples=100)
    def test_block_and_lock_are_independent(self, hand: list) -> None:
        """Blocking input and locking selection are independent states."""
        handler = InputHandler()

        handler.block_input()
        assert handler.input_blocked is True
        assert handler.selection_locked is False

        handler.lock_selection()
        assert handler.input_blocked is True
        assert handler.selection_locked is True

        handler.unblock_input()
        assert handler.input_blocked is False
        assert handler.selection_locked is True

        handler.unlock_selection()
        assert handler.input_blocked is False
        assert handler.selection_locked is False

    @given(block_count=st.integers(min_value=1, max_value=5))
    @settings(max_examples=100)
    def test_multiple_blocks_single_unblock(self, block_count: int) -> None:
        """Multiple block_input calls should all be cleared by a single unblock."""
        handler = InputHandler()
        for _ in range(block_count):
            handler.block_input()
        assert handler.input_blocked is True

        handler.unblock_input()
        assert handler.input_blocked is False
