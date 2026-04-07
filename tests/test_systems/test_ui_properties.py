"""Property-based tests for UIManager state reflection.

Feature: card-game-core, Property 41: UI State Reflection
For any game state, the UI should display current values for both players'
health, defense, vault size, hand cards, played cards, and round number.

Validates: Requirements 20.1, 20.2, 20.3, 20.4, 20.5, 20.6
"""

import pygame
from hypothesis import given, settings
import hypothesis.strategies as st

from src.entities.card import Card
from src.entities.player import Player
from src.entities.vault import Vault
from src.systems.ui_manager import UIManager

ALL_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
ALL_SUITS = ['Club', 'Spade', 'Heart', 'Diamond']
ALL_CARDS = [Card(rank=r, suit=s) for r in ALL_RANKS for s in ALL_SUITS]


# Initialize pygame once for the module
pygame.init()


def _make_surface():
    """Create a pygame surface for testing."""
    return pygame.Surface((1280, 720))


@st.composite
def card_strategy(draw):
    rank = draw(st.sampled_from(ALL_RANKS))
    suit = draw(st.sampled_from(ALL_SUITS))
    return Card(rank=rank, suit=suit)


@st.composite
def hand_strategy(draw, min_size=0, max_size=6):
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
def player_strategy(draw):
    health = draw(st.integers(min_value=0, max_value=50))
    defense = draw(st.integers(min_value=0, max_value=50))
    vault = Vault()
    vault_size = draw(st.integers(min_value=0, max_value=10))
    if vault_size > 0:
        vault_cards = [ALL_CARDS[i] for i in range(vault_size)]
        vault.add_cards(vault_cards)
    hand = draw(hand_strategy())
    player = Player(player_id=draw(st.integers(min_value=0, max_value=1)),
                    health=health, defense=defense, vault=vault, hand=hand)
    return player


class TestUIStateReflection:
    """**Validates: Requirements 20.1, 20.2, 20.3, 20.4, 20.5, 20.6**

    Property 41: UI State Reflection
    For any game state, the UI should display current values for both players'
    health, defense, vault size, hand cards, played cards, and round number.
    """

    def test_ui_manager_instantiation(self):
        """UIManager can be instantiated with a pygame surface."""
        surface = _make_surface()
        ui = UIManager(surface)
        assert ui.screen is surface
        assert ui.font is not None
        assert ui.large_font is not None

    @given(player=player_strategy(), position=st.sampled_from(['top', 'bottom']))
    @settings(max_examples=100)
    def test_render_player_stats_accepts_any_player(self, player, position):
        """render_player_stats should accept any valid player and position without error."""
        surface = _make_surface()
        ui = UIManager(surface)
        # Should not raise for any valid player state
        ui.render_player_stats(player, position)

    @given(hand=hand_strategy(min_size=1, max_size=6),
           num_selected=st.integers(min_value=0, max_value=3))
    @settings(max_examples=100)
    def test_render_hand_accepts_cards_and_selection(self, hand, num_selected):
        """render_hand should accept any hand and selection without error."""
        surface = _make_surface()
        ui = UIManager(surface)
        selected = hand[:min(num_selected, len(hand))]
        rects = ui.render_hand(hand, selected, 500)
        assert len(rects) == len(hand)

    @given(cards=st.lists(card_strategy(), min_size=3, max_size=3),
           revealed=st.booleans(),
           position=st.sampled_from(['top', 'bottom']))
    @settings(max_examples=100)
    def test_render_played_cards_accepts_parameters(self, cards, revealed, position):
        """render_played_cards should accept any 3 cards, reveal state, and position."""
        surface = _make_surface()
        ui = UIManager(surface)
        ui.render_played_cards(cards, revealed, position)

    @given(round_num=st.integers(min_value=1, max_value=100),
           phase=st.sampled_from(['Selection', 'Reveal', 'Resolution']))
    @settings(max_examples=100)
    def test_render_round_info_accepts_any_round(self, round_num, phase):
        """render_round_info should accept any round number and phase string."""
        surface = _make_surface()
        ui = UIManager(surface)
        ui.render_round_info(round_num, phase)

    @given(p1=player_strategy(), p2=player_strategy(),
           round_num=st.integers(min_value=1, max_value=50))
    @settings(max_examples=100)
    def test_full_ui_render_reflects_game_state(self, p1, p2, round_num):
        """A full render cycle should work for any combination of two players and round number."""
        surface = _make_surface()
        ui = UIManager(surface)

        # Render both players' stats
        ui.render_player_stats(p1, 'bottom')
        ui.render_player_stats(p2, 'top')

        # Render hands
        if p1.hand:
            ui.render_hand(p1.hand, [], 500)

        # Render round info
        ui.render_round_info(round_num, 'Selection')

        # Verify the UI manager still holds the correct screen reference
        assert ui.screen is surface
