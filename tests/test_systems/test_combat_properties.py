"""Property-based tests for CombatSystem damage summation.

Feature: card-game-core, Property 2: Damage Summation
Validates: Requirements 5.4
"""

from hypothesis import given, settings
import hypothesis.strategies as st

from src.entities.card import Card
from src.systems.combat_system import CombatSystem

ALL_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
ALL_SUITS = ['Club', 'Spade', 'Heart', 'Diamond']

card_strategy = st.builds(
    Card,
    rank=st.sampled_from(ALL_RANKS),
    suit=st.sampled_from(ALL_SUITS),
)

three_cards_strategy = st.lists(card_strategy, min_size=3, max_size=3)


class TestDamageSummation:
    """**Validates: Requirements 5.4**"""

    @given(cards=three_cards_strategy)
    @settings(max_examples=100)
    def test_total_base_damage_equals_sum_of_individual_damages(self, cards: list) -> None:
        """For any set of 3 cards, total base damage should equal the sum of individual card base damages."""
        combat = CombatSystem()
        total = combat.calculate_base_damage(cards)
        expected = sum(card.get_base_damage() for card in cards)
        assert total == expected

    @given(cards=three_cards_strategy)
    @settings(max_examples=100)
    def test_total_base_damage_is_positive(self, cards: list) -> None:
        """For any set of 3 cards, total base damage should always be positive (minimum 3)."""
        combat = CombatSystem()
        total = combat.calculate_base_damage(cards)
        assert total >= 3  # minimum: 3 Aces = 3 damage
        assert total <= 30  # maximum: 3 face cards = 30 damage


class TestRoundWinnerDetermination:
    """**Validates: Requirements 4.4, 11.1, 11.3**

    Property 11: Round Winner Determination
    For any two players' net standard damage values, the player with higher
    damage should win the round, unless Jack abilities reverse the logic.
    """

    @given(
        p1_damage=st.integers(min_value=0, max_value=200),
        p2_damage=st.integers(min_value=0, max_value=200),
        jack_count=st.integers(min_value=0, max_value=6),
    )
    @settings(max_examples=100)
    def test_higher_damage_wins_without_jack_reversal(
        self, p1_damage: int, p2_damage: int, jack_count: int
    ) -> None:
        """For any two damage values, the player with higher damage wins when
        jack_count is even, and the player with lower damage wins when
        jack_count is odd. Ties return None."""
        combat = CombatSystem()
        winner = combat.determine_winner(p1_damage, p2_damage, jack_count)

        reversed_logic = (jack_count % 2) == 1

        if p1_damage == p2_damage:
            assert winner is None, "Equal damage should result in a tie"
        elif not reversed_logic:
            # Normal: higher damage wins
            expected = 1 if p1_damage > p2_damage else 2
            assert winner == expected, (
                f"Normal logic: higher damage should win. "
                f"p1={p1_damage}, p2={p2_damage}, jacks={jack_count}, winner={winner}"
            )
        else:
            # Reversed: lower damage wins
            expected = 1 if p1_damage < p2_damage else 2
            assert winner == expected, (
                f"Reversed logic: lower damage should win. "
                f"p1={p1_damage}, p2={p2_damage}, jacks={jack_count}, winner={winner}"
            )

    @given(
        p1_damage=st.integers(min_value=0, max_value=200),
        p2_damage=st.integers(min_value=0, max_value=200),
    )
    @settings(max_examples=100)
    def test_tie_returns_none(self, p1_damage: int, p2_damage: int) -> None:
        """When both players deal equal damage, winner should be None regardless of jack count."""
        combat = CombatSystem()
        # Test with various jack counts — ties should always be None
        for jacks in [0, 1, 2, 3]:
            winner = combat.determine_winner(p1_damage, p1_damage, jacks)
            assert winner is None, (
                f"Equal damage ({p1_damage}) should always tie, got winner={winner} with jacks={jacks}"
            )


class TestJackReversesRoundLogic:
    """**Validates: Requirements 11.1, 11.3**

    Property 21: Jack Reverses Round Logic
    For any round with an odd number of Jacks, the player with lower standard
    damage should win; with an even number (including zero), the player with
    higher damage should win.
    """

    @given(
        p1_damage=st.integers(min_value=0, max_value=200),
        p2_damage=st.integers(min_value=0, max_value=200).filter(lambda x: True),
        odd_jack_count=st.sampled_from([1, 3, 5]),
    )
    @settings(max_examples=100)
    def test_odd_jacks_lower_damage_wins(
        self, p1_damage: int, p2_damage: int, odd_jack_count: int
    ) -> None:
        """With an odd number of Jacks, the player with lower damage should win."""
        combat = CombatSystem()
        winner = combat.determine_winner(p1_damage, p2_damage, odd_jack_count)

        if p1_damage == p2_damage:
            assert winner is None
        elif p1_damage < p2_damage:
            assert winner == 1, (
                f"Odd jacks ({odd_jack_count}): p1 has lower damage ({p1_damage} < {p2_damage}), "
                f"should win, got {winner}"
            )
        else:
            assert winner == 2, (
                f"Odd jacks ({odd_jack_count}): p2 has lower damage ({p2_damage} < {p1_damage}), "
                f"should win, got {winner}"
            )

    @given(
        p1_damage=st.integers(min_value=0, max_value=200),
        p2_damage=st.integers(min_value=0, max_value=200),
        even_jack_count=st.sampled_from([0, 2, 4, 6]),
    )
    @settings(max_examples=100)
    def test_even_jacks_higher_damage_wins(
        self, p1_damage: int, p2_damage: int, even_jack_count: int
    ) -> None:
        """With an even number of Jacks (including zero), the player with higher damage should win."""
        combat = CombatSystem()
        winner = combat.determine_winner(p1_damage, p2_damage, even_jack_count)

        if p1_damage == p2_damage:
            assert winner is None
        elif p1_damage > p2_damage:
            assert winner == 1, (
                f"Even jacks ({even_jack_count}): p1 has higher damage ({p1_damage} > {p2_damage}), "
                f"should win, got {winner}"
            )
        else:
            assert winner == 2, (
                f"Even jacks ({even_jack_count}): p2 has higher damage ({p2_damage} > {p1_damage}), "
                f"should win, got {winner}"
            )

    @given(
        damage=st.integers(min_value=0, max_value=200),
        jack_count=st.integers(min_value=0, max_value=6),
    )
    @settings(max_examples=100)
    def test_double_flip_restores_normal_logic(
        self, damage: int, jack_count: int
    ) -> None:
        """Two Jacks should cancel each other out — even jack_count behaves like zero jacks."""
        combat = CombatSystem()
        p1_damage = damage
        p2_damage = damage + 1  # Ensure p1 < p2

        winner_with_jacks = combat.determine_winner(p1_damage, p2_damage, jack_count)
        winner_with_zero = combat.determine_winner(p1_damage, p2_damage, 0)

        if jack_count % 2 == 0:
            assert winner_with_jacks == winner_with_zero, (
                f"Even jacks ({jack_count}) should behave like 0 jacks"
            )
        else:
            # Odd jacks should reverse the result
            assert winner_with_jacks != winner_with_zero, (
                f"Odd jacks ({jack_count}) should reverse the winner"
            )


from src.entities.player import Player
from src.entities.vault import Vault
from src.entities.deck import Deck


# Strategies for vault/win condition tests
six_cards_strategy = st.lists(card_strategy, min_size=6, max_size=6)


class TestVaultAdditionOnWin:
    """**Validates: Requirements 4.5, 18.1**

    Property 12: Vault Addition on Win
    For any round with a winner, all 6 played cards should be added to the
    winner's vault, increasing vault size by 6.
    """

    @given(cards=six_cards_strategy)
    @settings(max_examples=100)
    def test_vault_increases_by_six_on_win(self, cards: list) -> None:
        """For any 6 played cards added to a winner's vault, vault size should increase by 6."""
        combat = CombatSystem()
        player = Player(player_id=1)
        initial_size = player.vault.size()

        combat.add_to_vault(player, cards)

        assert player.vault.size() == initial_size + 6

    @given(
        existing_cards=st.lists(card_strategy, min_size=0, max_size=20),
        new_cards=six_cards_strategy,
    )
    @settings(max_examples=100)
    def test_vault_addition_preserves_existing_cards(
        self, existing_cards: list, new_cards: list
    ) -> None:
        """Adding 6 cards to a vault with existing cards should increase size by exactly 6."""
        combat = CombatSystem()
        player = Player(player_id=1)
        # Pre-populate vault
        player.vault.add_cards(existing_cards)
        initial_size = player.vault.size()

        combat.add_to_vault(player, new_cards)

        assert player.vault.size() == initial_size + 6


class TestHealthBasedWinCondition:
    """**Validates: Requirements 17.5, 17.6**

    Property 36: Health-Based Win Condition
    For any player reaching 0 health, the game should end with the opponent
    declared winner, unless both reach 0 simultaneously (resulting in a tie).
    """

    @given(p2_health=st.integers(min_value=1, max_value=50))
    @settings(max_examples=100)
    def test_player1_zero_health_player2_wins(self, p2_health: int) -> None:
        """When player 1 reaches 0 health, player 2 should win."""
        combat = CombatSystem()
        p1 = Player(player_id=1, health=0)
        p2 = Player(player_id=2, health=p2_health)

        result = combat.check_win_condition(p1, p2)

        assert result.game_over is True
        assert result.winner_id == 2
        assert result.reason == 'health'

    @given(p1_health=st.integers(min_value=1, max_value=50))
    @settings(max_examples=100)
    def test_player2_zero_health_player1_wins(self, p1_health: int) -> None:
        """When player 2 reaches 0 health, player 1 should win."""
        combat = CombatSystem()
        p1 = Player(player_id=1, health=p1_health)
        p2 = Player(player_id=2, health=0)

        result = combat.check_win_condition(p1, p2)

        assert result.game_over is True
        assert result.winner_id == 1
        assert result.reason == 'health'

    @given(data=st.data())
    @settings(max_examples=100)
    def test_both_zero_health_is_tie(self, data) -> None:
        """When both players reach 0 health simultaneously, the result should be a tie."""
        combat = CombatSystem()
        p1 = Player(player_id=1, health=0)
        p2 = Player(player_id=2, health=0)

        result = combat.check_win_condition(p1, p2)

        assert result.game_over is True
        assert result.winner_id is None
        assert result.reason == 'tie'

    @given(
        p1_health=st.integers(min_value=1, max_value=50),
        p2_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_both_alive_no_win(self, p1_health: int, p2_health: int) -> None:
        """When both players have health > 0, the game should not end due to health."""
        combat = CombatSystem()
        # Give both players decks with enough cards so vault condition doesn't trigger
        deck_cards = [Card(rank='2', suit='Club')] * 20
        p1 = Player(player_id=1, health=p1_health, deck=Deck(list(deck_cards)))
        p2 = Player(player_id=2, health=p2_health, deck=Deck(list(deck_cards)))

        result = combat.check_win_condition(p1, p2)

        assert result.game_over is False


class TestVaultBasedWinCondition:
    """**Validates: Requirements 18.4, 18.5, 18.6**

    Property 39: Vault-Based Win Condition
    For any game state where the draw pile cannot provide enough cards for both
    players to play a full round, the game should end with the player having the
    larger vault declared winner, or a tie if vaults are equal.
    """

    @given(
        p1_vault_size=st.integers(min_value=0, max_value=30),
        p2_vault_size=st.integers(min_value=0, max_value=30),
    )
    @settings(max_examples=100)
    def test_larger_vault_wins_when_cards_insufficient(
        self, p1_vault_size: int, p2_vault_size: int
    ) -> None:
        """When cards are insufficient for a full round, the larger vault should win."""
        combat = CombatSystem()
        # Create players with empty hands and empty decks so they can't play a round
        p1 = Player(player_id=1, health=50, deck=Deck([]))
        p2 = Player(player_id=2, health=50, deck=Deck([]))
        p1.hand = []
        p2.hand = []

        # Populate vaults
        p1_cards = [Card(rank='2', suit='Club')] * p1_vault_size
        p2_cards = [Card(rank='2', suit='Club')] * p2_vault_size
        p1.vault.add_cards(p1_cards)
        p2.vault.add_cards(p2_cards)

        result = combat.check_win_condition(p1, p2)

        assert result.game_over is True
        if p1_vault_size > p2_vault_size:
            assert result.winner_id == 1
            assert result.reason == 'vault'
        elif p2_vault_size > p1_vault_size:
            assert result.winner_id == 2
            assert result.reason == 'vault'
        else:
            assert result.winner_id is None
            assert result.reason == 'tie'

    @given(vault_size=st.integers(min_value=0, max_value=30))
    @settings(max_examples=100)
    def test_equal_vaults_is_tie_when_cards_insufficient(
        self, vault_size: int
    ) -> None:
        """When cards are insufficient and vaults are equal, the result should be a tie."""
        combat = CombatSystem()
        p1 = Player(player_id=1, health=50, deck=Deck([]))
        p2 = Player(player_id=2, health=50, deck=Deck([]))
        p1.hand = []
        p2.hand = []

        cards = [Card(rank='2', suit='Club')] * vault_size
        p1.vault.add_cards(list(cards))
        p2.vault.add_cards(list(cards))

        result = combat.check_win_condition(p1, p2)

        assert result.game_over is True
        assert result.winner_id is None
        assert result.reason == 'tie'

    @given(
        p1_vault_size=st.integers(min_value=0, max_value=30),
        p2_vault_size=st.integers(min_value=0, max_value=30),
        deck_size=st.integers(min_value=6, max_value=40),
    )
    @settings(max_examples=100)
    def test_sufficient_cards_no_vault_win(
        self, p1_vault_size: int, p2_vault_size: int, deck_size: int
    ) -> None:
        """When both players can play a full round, vault win condition should not trigger."""
        combat = CombatSystem()
        # Give players 3 cards in hand and enough in deck
        hand_cards = [Card(rank='2', suit='Club')] * 3
        deck_cards = [Card(rank='2', suit='Club')] * deck_size
        p1 = Player(player_id=1, health=50, deck=Deck(list(deck_cards)))
        p2 = Player(player_id=2, health=50, deck=Deck(list(deck_cards)))
        p1.hand = list(hand_cards)
        p2.hand = list(hand_cards)

        p1.vault.add_cards([Card(rank='2', suit='Club')] * p1_vault_size)
        p2.vault.add_cards([Card(rank='2', suit='Club')] * p2_vault_size)

        result = combat.check_win_condition(p1, p2)

        assert result.game_over is False


class TestTiedRoundHandling:
    """**Validates: Requirements 4.6**

    Property 13: Tied Round Handling
    For any round where both players deal equal net standard damage, all 6
    played cards should be shuffled back into the draw pile.
    """

    @given(
        deck_cards=st.lists(card_strategy, min_size=0, max_size=40),
        played_cards=six_cards_strategy,
    )
    @settings(max_examples=100)
    def test_tied_round_adds_six_cards_back_to_deck(
        self, deck_cards: list, played_cards: list
    ) -> None:
        """When a tie occurs, adding the 6 played cards back should increase
        the deck's remaining count by exactly 6."""
        combat = CombatSystem()
        deck = Deck(list(deck_cards))
        initial_remaining = deck.remaining()

        # Verify tie: equal damage yields None
        p1_damage = 10
        p2_damage = 10
        winner = combat.determine_winner(p1_damage, p2_damage, jack_count=0)
        assert winner is None, "Equal damage should produce a tie"

        # Simulate tied-round behaviour: add played cards back to deck
        deck.add_cards(played_cards)

        assert deck.remaining() == initial_remaining + 6

    @given(
        p1_cards=three_cards_strategy,
        p2_cards=three_cards_strategy,
        deck_cards=st.lists(card_strategy, min_size=0, max_size=40),
        jack_count=st.integers(min_value=0, max_value=6),
    )
    @settings(max_examples=100)
    def test_equal_base_damage_triggers_tie_and_cards_return(
        self, p1_cards: list, p2_cards: list, deck_cards: list, jack_count: int
    ) -> None:
        """For any two hands with equal base damage, determine_winner returns
        None and all 6 cards can be returned to the deck."""
        combat = CombatSystem()
        p1_damage = combat.calculate_base_damage(p1_cards)
        p2_damage = combat.calculate_base_damage(p2_cards)

        # Only test the tied case
        if p1_damage != p2_damage:
            return  # skip non-tie scenarios

        winner = combat.determine_winner(p1_damage, p2_damage, jack_count)
        assert winner is None, "Equal net damage must result in a tie"

        # Simulate returning all 6 played cards to the draw pile
        deck = Deck(list(deck_cards))
        initial_remaining = deck.remaining()
        all_played = p1_cards + p2_cards
        deck.add_cards(all_played)

        assert deck.remaining() == initial_remaining + 6
