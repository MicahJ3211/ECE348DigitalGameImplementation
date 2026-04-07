"""Property-based tests for Ace and Queen abilities in AbilityResolver.

Feature: card-game-core, Property 20: Ace Disables Face Abilities
Feature: card-game-core, Property 24: Queen Ability Disabling
Validates: Requirements 10.1, 10.4, 12.1, 12.2, 12.3
"""

from hypothesis import given, settings, assume
import hypothesis.strategies as st

from src.entities.card import Card
from src.entities.player import Player
from src.entities.vault import Vault
from src.systems.ability_resolver import AbilityResolver
from src.systems.combat_system import CombatSystem

ALL_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
FACE_RANKS = ['J', 'Q', 'K']
NUMBERED_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
ALL_SUITS = ['Club', 'Spade', 'Heart', 'Diamond']

card_strategy = st.builds(
    Card,
    rank=st.sampled_from(ALL_RANKS),
    suit=st.sampled_from(ALL_SUITS),
)

non_ace_card_strategy = st.builds(
    Card,
    rank=st.sampled_from(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']),
    suit=st.sampled_from(ALL_SUITS),
)

numbered_card_strategy = st.builds(
    Card,
    rank=st.sampled_from(NUMBERED_RANKS),
    suit=st.sampled_from(ALL_SUITS),
)

face_card_strategy = st.builds(
    Card,
    rank=st.sampled_from(FACE_RANKS),
    suit=st.sampled_from(ALL_SUITS),
)

ace_strategy = st.builds(
    Card,
    rank=st.just('A'),
    suit=st.sampled_from(ALL_SUITS),
)


def make_player(player_id: int, vault_size: int = 0) -> Player:
    """Create a player with a vault of the given size."""
    player = Player(player_id=player_id)
    if vault_size > 0:
        filler = [Card(rank='2', suit='Club')] * vault_size
        player.vault.add_cards(filler)
    return player



class TestAceDisablesFaceAbilities:
    """**Validates: Requirements 10.1, 10.4**

    Property 20: Ace Disables Face Abilities
    For any round where an Ace is played, Jack and King abilities
    should be disabled, but suit abilities should still activate.
    Queen resolves before Ace so is not affected.
    """

    @given(
        ace_suit=st.sampled_from(ALL_SUITS),
        other_cards_p1=st.lists(non_ace_card_strategy, min_size=2, max_size=2),
        cards_p2=st.lists(card_strategy, min_size=3, max_size=3),
    )
    @settings(max_examples=100)
    def test_ace_disables_jack_and_king_abilities(
        self, ace_suit: str, other_cards_p1: list, cards_p2: list
    ) -> None:
        """When an Ace is played, all J and K cards in both
        players' hands should have their indices added to disabled_abilities."""
        resolver = AbilityResolver(CombatSystem())
        ace = Card(rank='A', suit=ace_suit)
        cards1 = [ace] + other_cards_p1

        p1 = make_player(1)
        p2 = make_player(2)
        players = [p1, p2]
        cards = [cards1, cards_p2]
        disabled_abilities = {}

        resolver.execute_pre_reveal_abilities(players, cards, disabled_abilities)

        # Every J and K in both hands must be disabled (Q resolves before Ace)
        for i, player_cards in enumerate(cards):
            for j, card in enumerate(player_cards):
                if card.rank in ['J', 'K']:
                    assert i in disabled_abilities, (
                        f"Player {i} should have disabled abilities dict entry"
                    )
                    assert j in disabled_abilities[i], (
                        f"Card index {j} ({card}) for player {i} should be disabled"
                    )

    @given(
        ace_suit=st.sampled_from(ALL_SUITS),
        numbered_cards_p1=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        numbered_cards_p2=st.lists(numbered_card_strategy, min_size=3, max_size=3),
    )
    @settings(max_examples=100)
    def test_ace_does_not_disable_suit_abilities(
        self, ace_suit: str, numbered_cards_p1: list, numbered_cards_p2: list
    ) -> None:
        """When an Ace is played and all other cards are numbered, no cards
        should be disabled — suit abilities remain active."""
        resolver = AbilityResolver(CombatSystem())
        ace = Card(rank='A', suit=ace_suit)
        cards1 = [ace] + numbered_cards_p1

        p1 = make_player(1)
        p2 = make_player(2)
        players = [p1, p2]
        cards = [cards1, numbered_cards_p2]
        disabled_abilities = {}

        resolver.execute_pre_reveal_abilities(players, cards, disabled_abilities)

        # Numbered cards should NOT be disabled (suit abilities still active)
        for i, player_cards in enumerate(cards):
            for j, card in enumerate(player_cards):
                if card.is_numbered_card():
                    is_disabled = i in disabled_abilities and j in disabled_abilities[i]
                    assert not is_disabled, (
                        f"Numbered card {card} at index {j} for player {i} "
                        f"should NOT be disabled by Ace"
                    )

    @given(
        ace_suit_p1=st.sampled_from(ALL_SUITS),
        ace_suit_p2=st.sampled_from(ALL_SUITS),
        other_p1=st.lists(card_strategy, min_size=2, max_size=2),
        other_p2=st.lists(card_strategy, min_size=2, max_size=2),
    )
    @settings(max_examples=100)
    def test_ace_from_either_player_disables_face_cards(
        self, ace_suit_p1: str, ace_suit_p2: str, other_p1: list, other_p2: list
    ) -> None:
        """When both players play an Ace, all J and K cards should be disabled."""
        resolver = AbilityResolver(CombatSystem())
        cards1 = [Card(rank='A', suit=ace_suit_p1)] + other_p1
        cards2 = [Card(rank='A', suit=ace_suit_p2)] + other_p2

        p1 = make_player(1)
        p2 = make_player(2)
        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities = {}

        resolver.execute_pre_reveal_abilities(players, cards, disabled_abilities)

        for i, player_cards in enumerate(cards):
            for j, card in enumerate(player_cards):
                if card.rank in ['J', 'K']:
                    assert i in disabled_abilities and j in disabled_abilities[i], (
                        f"Card {card} at ({i},{j}) should be disabled when Ace is present"
                    )

    @given(
        ace_suit=st.sampled_from(ALL_SUITS),
    )
    @settings(max_examples=100)
    def test_ace_does_not_disable_ace_itself(
        self, ace_suit: str
    ) -> None:
        """The Ace card itself should not appear in disabled_abilities (Ace is
        not J or K). Use only numbered cards alongside to isolate the test."""
        resolver = AbilityResolver(CombatSystem())
        ace = Card(rank='A', suit=ace_suit)
        jack = Card(rank='J', suit='Club')
        cards1 = [ace, jack, Card(rank='2', suit='Heart')]
        cards2 = [Card(rank='3', suit='Heart'), Card(rank='4', suit='Heart'), Card(rank='5', suit='Heart')]

        p1 = make_player(1)
        p2 = make_player(2)
        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities = {}

        resolver.execute_pre_reveal_abilities(players, cards, disabled_abilities)

        # Index 0 is the Ace — it should NOT be disabled
        ace_disabled = 0 in disabled_abilities.get(0, [])
        assert not ace_disabled, "Ace itself should not be in disabled_abilities"
        # Index 1 is the Jack — it SHOULD be disabled
        jack_disabled = 1 in disabled_abilities.get(0, [])
        assert jack_disabled, "Jack should be disabled by Ace"


class TestQueenAbilityDisabling:
    """**Validates: Requirements 12.1, 12.2, 12.3**

    Property 24: Queen Ability Disabling
    For any Queen played, the player should be able to disable 2 opponent
    abilities if their vault is smaller, or 1 opponent ability if their vault
    is larger or equal.
    """

    @given(
        queen_suit=st.sampled_from(ALL_SUITS),
        other_cards=st.lists(non_ace_card_strategy, min_size=2, max_size=2),
        opponent_cards=st.lists(
            st.builds(Card, rank=st.sampled_from(NUMBERED_RANKS), suit=st.sampled_from(ALL_SUITS)),
            min_size=3, max_size=3,
        ),
        p1_vault_size=st.integers(min_value=0, max_value=20),
        p2_vault_size=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=100)
    def test_queen_disables_correct_number_of_opponent_abilities(
        self, queen_suit: str, other_cards: list, opponent_cards: list,
        p1_vault_size: int, p2_vault_size: int
    ) -> None:
        """Queen should disable 2 opponent abilities when player vault is smaller,
        or 1 when vault is larger or equal."""
        # Filter out Aces from other_cards to avoid Ace overriding Queen
        other_cards = [c for c in other_cards if c.rank != 'A']
        assume(len(other_cards) == 2)

        resolver = AbilityResolver(CombatSystem())
        queen = Card(rank='Q', suit=queen_suit)
        cards1 = [queen] + other_cards

        p1 = make_player(1, vault_size=p1_vault_size)
        p2 = make_player(2, vault_size=p2_vault_size)
        players = [p1, p2]
        cards = [cards1, opponent_cards]
        disabled_abilities = {}

        resolver.execute_pre_reveal_abilities(players, cards, disabled_abilities)

        expected_disable_count = 2 if p1_vault_size < p2_vault_size else 1

        # Opponent (player index 1) should have abilities disabled
        actual_disabled = len(disabled_abilities.get(1, []))
        # The actual count is min(expected, number of opponent cards)
        expected = min(expected_disable_count, len(opponent_cards))
        assert actual_disabled == expected, (
            f"Expected {expected} disabled abilities for opponent, got {actual_disabled}. "
            f"p1_vault={p1_vault_size}, p2_vault={p2_vault_size}"
        )

    @given(
        queen_suit=st.sampled_from(ALL_SUITS),
        other_cards=st.lists(non_ace_card_strategy, min_size=2, max_size=2),
        opponent_cards=st.lists(card_strategy, min_size=3, max_size=3),
        vault_size=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=100)
    def test_queen_smaller_vault_disables_two(
        self, queen_suit: str, other_cards: list, opponent_cards: list, vault_size: int
    ) -> None:
        """When the Queen player has a strictly smaller vault, 2 opponent abilities
        should be disabled."""
        other_cards = [c for c in other_cards if c.rank != 'A']
        assume(len(other_cards) == 2)
        # Also ensure opponent has no Ace (which would override Queen)
        assume(all(c.rank != 'A' for c in opponent_cards))

        resolver = AbilityResolver(CombatSystem())
        queen = Card(rank='Q', suit=queen_suit)
        cards1 = [queen] + other_cards

        p1 = make_player(1, vault_size=vault_size)
        p2 = make_player(2, vault_size=vault_size + 1)  # opponent has larger vault
        players = [p1, p2]
        cards = [cards1, opponent_cards]
        disabled_abilities = {}

        resolver.execute_pre_reveal_abilities(players, cards, disabled_abilities)

        actual_disabled = len(disabled_abilities.get(1, []))
        expected = min(2, len(opponent_cards))
        assert actual_disabled == expected, (
            f"Smaller vault: expected {expected} disabled, got {actual_disabled}"
        )

    @given(
        queen_suit=st.sampled_from(ALL_SUITS),
        other_cards=st.lists(non_ace_card_strategy, min_size=2, max_size=2),
        opponent_cards=st.lists(card_strategy, min_size=3, max_size=3),
        vault_size=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=100)
    def test_queen_larger_or_equal_vault_disables_one(
        self, queen_suit: str, other_cards: list, opponent_cards: list, vault_size: int
    ) -> None:
        """When the Queen player has a larger or equal vault, 1 opponent ability
        should be disabled."""
        other_cards = [c for c in other_cards if c.rank != 'A']
        assume(len(other_cards) == 2)
        assume(all(c.rank != 'A' for c in opponent_cards))

        resolver = AbilityResolver(CombatSystem())
        queen = Card(rank='Q', suit=queen_suit)
        cards1 = [queen] + other_cards

        # Equal vault
        p1 = make_player(1, vault_size=vault_size)
        p2 = make_player(2, vault_size=vault_size)
        players = [p1, p2]
        cards = [cards1, opponent_cards]
        disabled_abilities = {}

        resolver.execute_pre_reveal_abilities(players, cards, disabled_abilities)

        actual_disabled = len(disabled_abilities.get(1, []))
        expected = min(1, len(opponent_cards))
        assert actual_disabled == expected, (
            f"Equal vault: expected {expected} disabled, got {actual_disabled}"
        )

    @given(
        queen_suit=st.sampled_from(ALL_SUITS),
        other_cards=st.lists(non_ace_card_strategy, min_size=2, max_size=2),
        opponent_cards=st.lists(numbered_card_strategy, min_size=3, max_size=3),
        p1_vault_size=st.integers(min_value=0, max_value=20),
        p2_vault_size=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=100)
    def test_queen_does_not_disable_own_abilities(
        self, queen_suit: str, other_cards: list, opponent_cards: list,
        p1_vault_size: int, p2_vault_size: int
    ) -> None:
        """Queen should only disable opponent abilities, not the Queen player's own.
        Opponent cards are numbered only (no Queen/Ace) to isolate this property."""
        other_cards = [c for c in other_cards if c.rank != 'A']
        assume(len(other_cards) == 2)

        resolver = AbilityResolver(CombatSystem())
        queen = Card(rank='Q', suit=queen_suit)
        cards1 = [queen] + other_cards

        p1 = make_player(1, vault_size=p1_vault_size)
        p2 = make_player(2, vault_size=p2_vault_size)
        players = [p1, p2]
        cards = [cards1, opponent_cards]
        disabled_abilities = {}

        resolver.execute_pre_reveal_abilities(players, cards, disabled_abilities)

        # Player 0 (Queen player) should have NO disabled abilities
        assert len(disabled_abilities.get(0, [])) == 0, (
            f"Queen player should not have own abilities disabled, "
            f"but got {disabled_abilities.get(0, [])}"
        )

    @given(
        ace_suit=st.sampled_from(ALL_SUITS),
        queen_suit=st.sampled_from(ALL_SUITS),
        other_card=non_ace_card_strategy,
        opponent_cards=st.lists(card_strategy, min_size=3, max_size=3),
        p1_vault_size=st.integers(min_value=0, max_value=20),
        p2_vault_size=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=100)
    def test_ace_undoes_queen_disables(
        self, ace_suit: str, queen_suit: str, other_card,
        opponent_cards: list, p1_vault_size: int, p2_vault_size: int
    ) -> None:
        """Queen resolves first and disables opponent cards, but then Ace
        undoes Queen's effect — re-enabling those cards. The net result
        is that Queen's disables are removed when Ace is present."""
        # Ensure no extra Aces or Queens in other cards
        assume(other_card.rank not in ['A', 'Q'])
        assume(all(c.rank not in ['A', 'Q'] for c in opponent_cards))

        resolver = AbilityResolver(CombatSystem())
        # Player 1 has the Queen, Player 2 has the Ace
        queen = Card(rank='Q', suit=queen_suit)
        cards1 = [queen, other_card, Card(rank='2', suit='Club')]
        ace = Card(rank='A', suit=ace_suit)
        cards2 = [ace, opponent_cards[0] if len(opponent_cards) >= 1 else Card(rank='2', suit='Club'),
                  opponent_cards[1] if len(opponent_cards) >= 2 else Card(rank='3', suit='Club')]

        p1 = make_player(1, vault_size=p1_vault_size)
        p2 = make_player(2, vault_size=p2_vault_size)
        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities = {}

        resolver.execute_pre_reveal_abilities(players, cards, disabled_abilities)

        # Queen fired first and disabled some of player 2's cards,
        # but then Ace undid those disables. So player 2's cards that
        # Queen disabled should no longer be in disabled_abilities
        # (unless they are J/K which Ace re-disables for a different reason).
        # Cards that are NOT J or K should be fully re-enabled.
        for j, card in enumerate(cards2):
            if card.rank not in ['J', 'K']:
                is_disabled = 1 in disabled_abilities and j in disabled_abilities[1]
                assert not is_disabled, (
                    f"Card {card} at index {j} should be re-enabled by Ace "
                    f"(Queen's disable undone), but it's still disabled"
                )



class TestJackReversedDamageApplication:
    """**Validates: Requirements 11.2**

    Property 22: Jack Reversed Damage Application
    For any round with Jack reversal active, the loser should take damage equal
    to the difference between the two players' standard damage values.
    """

    @given(
        p1_damage=st.integers(min_value=0, max_value=100),
        p2_damage=st.integers(min_value=0, max_value=100),
        p1_health=st.integers(min_value=10, max_value=50),
        p2_health=st.integers(min_value=10, max_value=50),
    )
    @settings(max_examples=100)
    def test_jack_reversal_loser_takes_difference_damage(
        self, p1_damage: int, p2_damage: int, p1_health: int, p2_health: int
    ) -> None:
        """With an odd number of Jacks (reversal active), the player with
        HIGHER standard damage loses and takes damage equal to the difference."""
        assume(p1_damage != p2_damage)

        combat = CombatSystem()
        # Odd jack_count means reversal is active
        jack_count = 1
        winner_id = combat.determine_winner(p1_damage, p2_damage, jack_count)

        # Under reversal, lower damage wins
        damage_diff = abs(p1_damage - p2_damage)

        if p1_damage < p2_damage:
            # p1 has lower damage → p1 wins under reversal
            assert winner_id == 1
            # p2 is the loser; apply the difference as standard damage
            p2 = Player(player_id=2, health=p2_health, defense=0)
            p2.take_damage(standard_dmg=damage_diff, true_dmg=0)
            assert p2.health == max(0, p2_health - damage_diff)
        else:
            # p2 has lower damage → p2 wins under reversal
            assert winner_id == 2
            p1 = Player(player_id=1, health=p1_health, defense=0)
            p1.take_damage(standard_dmg=damage_diff, true_dmg=0)
            assert p1.health == max(0, p1_health - damage_diff)

    @given(
        damage=st.integers(min_value=0, max_value=100),
    )
    @settings(max_examples=100)
    def test_jack_reversal_equal_damage_is_tie(self, damage: int) -> None:
        """With Jack reversal active, equal damage should still result in a tie."""
        combat = CombatSystem()
        winner_id = combat.determine_winner(damage, damage, jack_count=1)
        assert winner_id is None


class TestJackDoesNotAffectKing:
    """**Validates: Requirements 11.4, 13.5**

    Property 23: Jack Does Not Affect King
    For any round with both Jack and King abilities, King's damage should
    apply normally regardless of Jack's reversal effect.
    """

    @given(
        vault_size=st.integers(min_value=0, max_value=50),
        opponent_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_king_damage_unaffected_by_jack(
        self, vault_size: int, opponent_health: int
    ) -> None:
        """When both Jack and King are played (not disabled), King should still
        deal damage equal to the opponent's vault size (through defense)."""
        resolver = AbilityResolver(CombatSystem())

        # Player 0 plays Jack + King + a numbered card
        cards1 = [Card(rank='J', suit='Club'), Card(rank='K', suit='Spade'), Card(rank='2', suit='Heart')]
        # Player 1 plays numbered cards only
        cards2 = [Card(rank='3', suit='Club'), Card(rank='4', suit='Diamond'), Card(rank='5', suit='Heart')]

        p1 = make_player(1, vault_size=0)
        p2 = make_player(2, vault_size=vault_size)
        p2.health = opponent_health

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        jack_count, king_activated = resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        # Jack should be counted
        assert jack_count >= 1

        # King should have activated
        assert king_activated is True

        # King damage = vault_size, applied as standard damage (defense=0 so all hits health)
        expected_health = max(0, opponent_health - vault_size)
        assert p2.health == expected_health, (
            f"King damage should not be affected by Jack reversal. "
            f"Expected health={expected_health}, got {p2.health}"
        )

    @given(
        vault_size=st.integers(min_value=1, max_value=50),
        opponent_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_king_vault_reduction_unaffected_by_jack(
        self, vault_size: int, opponent_health: int
    ) -> None:
        """King's vault reduction (floor(V/4)) should apply normally even when
        Jack reversal is active."""
        resolver = AbilityResolver(CombatSystem())

        cards1 = [Card(rank='J', suit='Club'), Card(rank='K', suit='Spade'), Card(rank='2', suit='Heart')]
        cards2 = [Card(rank='3', suit='Club'), Card(rank='4', suit='Diamond'), Card(rank='5', suit='Heart')]

        p1 = make_player(1, vault_size=0)
        p2 = make_player(2, vault_size=vault_size)
        p2.health = opponent_health

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        expected_reduction = vault_size // 4
        expected_vault_after = vault_size - expected_reduction

        resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        assert p2.vault.size() == expected_vault_after, (
            f"Vault should be reduced by floor({vault_size}/4)={expected_reduction}. "
            f"Expected size={expected_vault_after}, got {p2.vault.size()}"
        )


class TestKingTrueDamageAndVaultReduction:
    """**Validates: Requirements 13.1, 13.2, 13.3**

    Property 25: King Damage and Vault Reduction
    For any King played against an opponent with vault size V, damage
    should equal V (applied as standard damage through defense), and the
    opponent's vault should be reduced by floor(V / 4) cards which are
    removed from the game.
    """

    @given(
        vault_size=st.integers(min_value=0, max_value=50),
        opponent_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_king_deals_damage_equal_to_vault_size(
        self, vault_size: int, opponent_health: int
    ) -> None:
        """King should deal damage equal to the opponent's vault size."""
        resolver = AbilityResolver(CombatSystem())

        cards1 = [Card(rank='K', suit='Club'), Card(rank='2', suit='Heart'), Card(rank='3', suit='Heart')]
        cards2 = [Card(rank='4', suit='Club'), Card(rank='5', suit='Diamond'), Card(rank='6', suit='Heart')]

        p1 = make_player(1, vault_size=0)
        p2 = make_player(2, vault_size=vault_size)
        p2.health = opponent_health

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        # King damage = vault_size, applied as standard damage (defense=0 so all hits health)
        expected_health = max(0, opponent_health - vault_size)
        assert p2.health == expected_health, (
            f"King damage should equal vault size {vault_size}. "
            f"Expected health={expected_health}, got {p2.health}"
        )

    @given(
        vault_size=st.integers(min_value=0, max_value=50),
    )
    @settings(max_examples=100)
    def test_king_reduces_vault_by_floor_quarter(self, vault_size: int) -> None:
        """King should reduce opponent's vault by floor(V / 4) cards."""
        resolver = AbilityResolver(CombatSystem())

        cards1 = [Card(rank='K', suit='Club'), Card(rank='2', suit='Heart'), Card(rank='3', suit='Heart')]
        cards2 = [Card(rank='4', suit='Club'), Card(rank='5', suit='Diamond'), Card(rank='6', suit='Heart')]

        p1 = make_player(1, vault_size=0)
        p2 = make_player(2, vault_size=vault_size)

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        expected_reduction = vault_size // 4
        expected_vault_after = vault_size - expected_reduction

        resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        assert p2.vault.size() == expected_vault_after, (
            f"Vault should be reduced by floor({vault_size}/4)={expected_reduction}. "
            f"Expected {expected_vault_after}, got {p2.vault.size()}"
        )

    @given(
        vault_size=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_king_removed_cards_are_gone_from_game(self, vault_size: int) -> None:
        """Cards removed by King should not remain in the vault."""
        resolver = AbilityResolver(CombatSystem())

        cards1 = [Card(rank='K', suit='Club'), Card(rank='2', suit='Heart'), Card(rank='3', suit='Heart')]
        cards2 = [Card(rank='4', suit='Club'), Card(rank='5', suit='Diamond'), Card(rank='6', suit='Heart')]

        p1 = make_player(1, vault_size=0)
        p2 = make_player(2, vault_size=vault_size)
        initial_vault_size = p2.vault.size()

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        removed_count = initial_vault_size - p2.vault.size()
        assert removed_count == vault_size // 4, (
            f"Expected {vault_size // 4} cards removed, but {removed_count} were removed"
        )


class TestKingAbilityNonStacking:
    """**Validates: Requirements 13.4**

    Property 26: King Ability Non-Stacking
    For any round where multiple Kings are played by the same player, the King
    ability should activate only once.
    """

    @given(
        vault_size=st.integers(min_value=4, max_value=50),
        opponent_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_multiple_kings_same_player_activate_once(
        self, vault_size: int, opponent_health: int
    ) -> None:
        """When a player plays 2 Kings, the King ability should only activate
        once — true damage and vault reduction applied only once."""
        resolver = AbilityResolver(CombatSystem())

        # Player 0 plays 2 Kings + a numbered card
        cards1 = [Card(rank='K', suit='Club'), Card(rank='K', suit='Spade'), Card(rank='2', suit='Heart')]
        cards2 = [Card(rank='3', suit='Club'), Card(rank='4', suit='Diamond'), Card(rank='5', suit='Heart')]

        p1 = make_player(1, vault_size=0)
        p2 = make_player(2, vault_size=vault_size)
        p2.health = opponent_health

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        expected_true_damage = vault_size  # only once
        expected_vault_reduction = vault_size // 4
        expected_vault_after = vault_size - expected_vault_reduction
        expected_health = max(0, opponent_health - expected_true_damage)

        jack_count, king_activated = resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        assert king_activated is True
        assert p2.health == expected_health, (
            f"King should activate once: damage={expected_true_damage}. "
            f"Expected health={expected_health}, got {p2.health}"
        )
        assert p2.vault.size() == expected_vault_after, (
            f"King should reduce vault once by {expected_vault_reduction}. "
            f"Expected vault={expected_vault_after}, got {p2.vault.size()}"
        )

    @given(
        vault_size_p1=st.integers(min_value=0, max_value=50),
        vault_size_p2=st.integers(min_value=0, max_value=50),
    )
    @settings(max_examples=100)
    def test_kings_from_different_players_activate_once_total(
        self, vault_size_p1: int, vault_size_p2: int
    ) -> None:
        """When both players play a King, the ability should still only activate
        once total (non-stacking across all players)."""
        resolver = AbilityResolver(CombatSystem())

        # Both players play a King
        cards1 = [Card(rank='K', suit='Club'), Card(rank='2', suit='Heart'), Card(rank='3', suit='Heart')]
        cards2 = [Card(rank='K', suit='Spade'), Card(rank='4', suit='Diamond'), Card(rank='5', suit='Heart')]

        p1 = make_player(1, vault_size=vault_size_p1)
        p2 = make_player(2, vault_size=vault_size_p2)
        p1_initial_health = p1.health
        p2_initial_health = p2.health

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        jack_count, king_activated = resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        assert king_activated is True

        # Only one King should have activated. Player 0's King activates first
        # (iteration order), targeting player 1.
        expected_true_damage_to_p2 = vault_size_p2
        expected_vault_reduction_p2 = vault_size_p2 // 4
        expected_p2_vault = vault_size_p2 - expected_vault_reduction_p2
        expected_p2_health = max(0, p2_initial_health - expected_true_damage_to_p2)

        assert p2.health == expected_p2_health, (
            f"First King (p1's) should target p2. Expected p2 health={expected_p2_health}, got {p2.health}"
        )
        assert p2.vault.size() == expected_p2_vault, (
            f"First King should reduce p2 vault. Expected={expected_p2_vault}, got {p2.vault.size()}"
        )

        # Player 1's King should NOT have activated (non-stacking)
        assert p1.health == p1_initial_health, (
            f"Second King should not activate. p1 health should remain {p1_initial_health}, got {p1.health}"
        )
        assert p1.vault.size() == vault_size_p1, (
            f"Second King should not activate. p1 vault should remain {vault_size_p1}, got {p1.vault.size()}"
        )


class TestClubAbilityDamageBonus:
    """**Validates: Requirements 6.1**

    Property 16: Club Ability Damage Bonus
    For any numbered Club card and any vault size, the damage bonus should
    equal floor(vault_size / 2).
    """

    @given(
        club_rank=st.sampled_from(NUMBERED_RANKS),
        other_cards=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        vault_size=st.integers(min_value=0, max_value=50),
    )
    @settings(max_examples=100)
    def test_club_damage_bonus_equals_floor_vault_div_2(
        self, club_rank: str, other_cards: list, vault_size: int
    ) -> None:
        """A numbered Club card should add floor(vault_size / 2) to damage_modifiers."""
        resolver = AbilityResolver(CombatSystem())
        club_card = Card(rank=club_rank, suit='Club')
        cards1 = [club_card] + other_cards
        # Opponent plays non-Club numbered cards to isolate the property
        cards2 = [Card(rank='2', suit='Heart'), Card(rank='3', suit='Heart'), Card(rank='4', suit='Heart')]

        p1 = make_player(1, vault_size=vault_size)
        p2 = make_player(2, vault_size=0)

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        expected_bonus = vault_size // 2
        # Count how many Club numbered cards player 0 has (the explicit one + any from other_cards)
        club_count = sum(1 for c in cards1 if c.is_numbered_card() and c.suit == 'Club')
        expected_total = expected_bonus * club_count

        assert damage_modifiers[0] == expected_total, (
            f"Club damage bonus should be floor({vault_size}/2)={expected_bonus} per Club card "
            f"({club_count} Club cards). Expected total={expected_total}, got {damage_modifiers[0]}"
        )

    @given(
        vault_size=st.integers(min_value=0, max_value=50),
    )
    @settings(max_examples=100)
    def test_club_bonus_uses_floor_division(self, vault_size: int) -> None:
        """The Club bonus must use floor division (integer division) of vault_size / 2."""
        resolver = AbilityResolver(CombatSystem())
        cards1 = [Card(rank='5', suit='Club'), Card(rank='2', suit='Heart'), Card(rank='3', suit='Heart')]
        cards2 = [Card(rank='4', suit='Heart'), Card(rank='5', suit='Heart'), Card(rank='6', suit='Heart')]

        p1 = make_player(1, vault_size=vault_size)
        p2 = make_player(2, vault_size=0)

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        expected = vault_size // 2
        assert damage_modifiers[0] == expected, (
            f"Club bonus should be floor({vault_size}/2)={expected}, got {damage_modifiers[0]}"
        )


class TestSpadeAbilityDefenseBonus:
    """**Validates: Requirements 7.1, 7.3**

    Property 17: Spade Ability Defense Bonus
    For any numbered Spade card and any vault size, the defense bonus should
    equal floor(vault_size / 2) and be added to current defense.
    """

    @given(
        spade_rank=st.sampled_from(NUMBERED_RANKS),
        other_cards=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        vault_size=st.integers(min_value=0, max_value=50),
        initial_defense=st.integers(min_value=0, max_value=50),
    )
    @settings(max_examples=100)
    def test_spade_defense_bonus_equals_floor_vault_div_2(
        self, spade_rank: str, other_cards: list, vault_size: int, initial_defense: int
    ) -> None:
        """A numbered Spade card should add floor(vault_size / 2) to defense_modifiers
        and to the player's actual defense."""
        resolver = AbilityResolver(CombatSystem())
        spade_card = Card(rank=spade_rank, suit='Spade')
        cards1 = [spade_card] + other_cards
        cards2 = [Card(rank='2', suit='Heart'), Card(rank='3', suit='Heart'), Card(rank='4', suit='Heart')]

        p1 = make_player(1, vault_size=vault_size)
        p1.defense = initial_defense
        p2 = make_player(2, vault_size=0)

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        expected_bonus = vault_size // 2
        # Count how many Spade numbered cards player 0 has
        spade_count = sum(1 for c in cards1 if c.is_numbered_card() and c.suit == 'Spade')
        expected_total_bonus = expected_bonus * spade_count

        assert defense_modifiers[0] == expected_total_bonus, (
            f"Spade defense bonus should be floor({vault_size}/2)={expected_bonus} per Spade card "
            f"({spade_count} Spade cards). Expected total={expected_total_bonus}, got {defense_modifiers[0]}"
        )

        # Defense should also be added to the player's actual defense
        expected_defense = initial_defense + expected_total_bonus
        assert p1.defense == expected_defense, (
            f"Player defense should be {initial_defense} + {expected_total_bonus} = {expected_defense}, "
            f"got {p1.defense}"
        )

    @given(
        vault_size=st.integers(min_value=0, max_value=50),
        initial_defense=st.integers(min_value=0, max_value=50),
    )
    @settings(max_examples=100)
    def test_spade_bonus_added_to_current_defense(
        self, vault_size: int, initial_defense: int
    ) -> None:
        """The Spade bonus should be added on top of the player's existing defense."""
        resolver = AbilityResolver(CombatSystem())
        cards1 = [Card(rank='7', suit='Spade'), Card(rank='2', suit='Heart'), Card(rank='3', suit='Heart')]
        cards2 = [Card(rank='4', suit='Heart'), Card(rank='5', suit='Heart'), Card(rank='6', suit='Heart')]

        p1 = make_player(1, vault_size=vault_size)
        p1.defense = initial_defense
        p2 = make_player(2, vault_size=0)

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        expected_bonus = vault_size // 2
        assert p1.defense == initial_defense + expected_bonus, (
            f"Defense should be {initial_defense} + floor({vault_size}/2)={expected_bonus} = "
            f"{initial_defense + expected_bonus}, got {p1.defense}"
        )


class TestDiamondAbilityVaultManipulation:
    """**Validates: Requirements 9.1, 9.2**

    Property 19: Diamond Ability Vault Manipulation
    For any numbered Diamond card, a random card should be removed from a
    non-empty vault and shuffled back into the draw pile.
    """

    @given(
        diamond_rank=st.sampled_from(NUMBERED_RANKS),
        other_cards=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        opponent_cards=st.lists(numbered_card_strategy, min_size=3, max_size=3),
        p1_vault_size=st.integers(min_value=1, max_value=30),
        p2_vault_size=st.integers(min_value=0, max_value=30),
    )
    @settings(max_examples=100)
    def test_diamond_removes_card_from_vault_and_adds_to_draw_pile(
        self, diamond_rank: str, other_cards: list, opponent_cards: list,
        p1_vault_size: int, p2_vault_size: int
    ) -> None:
        """When a numbered Diamond card is played and at least one vault is
        non-empty, a card should be removed from some vault and added to the
        draw pile."""
        from src.entities.deck import Deck

        resolver = AbilityResolver(CombatSystem())
        diamond = Card(rank=diamond_rank, suit='Diamond')
        # Ensure other cards are NOT Diamond to isolate a single trigger
        other_cards = [c for c in other_cards if c.suit != 'Diamond']
        assume(len(other_cards) == 2)
        opponent_cards = [c for c in opponent_cards if c.suit != 'Diamond']
        assume(len(opponent_cards) == 3)

        cards1 = [diamond] + other_cards

        p1 = make_player(1, vault_size=p1_vault_size)
        p2 = make_player(2, vault_size=p2_vault_size)
        draw_pile = Deck([])

        players = [p1, p2]
        cards = [cards1, opponent_cards]
        disabled_abilities: dict = {}

        total_vault_before = p1.vault.size() + p2.vault.size()
        draw_before = draw_pile.remaining()

        resolver.execute_diamond_ability(players, cards, disabled_abilities, draw_pile)

        total_vault_after = p1.vault.size() + p2.vault.size()

        # Exactly one card should have moved from a vault to the draw pile
        assert total_vault_after == total_vault_before - 1, (
            f"One card should be removed from vaults. Before={total_vault_before}, after={total_vault_after}"
        )
        assert draw_pile.remaining() == draw_before + 1, (
            f"Draw pile should gain 1 card. Before={draw_before}, after={draw_pile.remaining()}"
        )

    @given(
        diamond_rank=st.sampled_from(NUMBERED_RANKS),
        other_cards=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        opponent_cards=st.lists(numbered_card_strategy, min_size=3, max_size=3),
    )
    @settings(max_examples=100)
    def test_diamond_skips_when_both_vaults_empty(
        self, diamond_rank: str, other_cards: list, opponent_cards: list
    ) -> None:
        """When both vaults are empty, Diamond ability should skip without
        modifying the draw pile."""
        from src.entities.deck import Deck

        resolver = AbilityResolver(CombatSystem())
        diamond = Card(rank=diamond_rank, suit='Diamond')
        other_cards = [c for c in other_cards if c.suit != 'Diamond']
        assume(len(other_cards) == 2)
        opponent_cards = [c for c in opponent_cards if c.suit != 'Diamond']
        assume(len(opponent_cards) == 3)

        cards1 = [diamond] + other_cards

        p1 = make_player(1, vault_size=0)
        p2 = make_player(2, vault_size=0)
        draw_pile = Deck([])

        players = [p1, p2]
        cards = [cards1, opponent_cards]
        disabled_abilities: dict = {}

        resolver.execute_diamond_ability(players, cards, disabled_abilities, draw_pile)

        assert p1.vault.size() == 0
        assert p2.vault.size() == 0
        assert draw_pile.remaining() == 0, (
            "Draw pile should remain empty when both vaults are empty"
        )

    @given(
        diamond_rank=st.sampled_from(NUMBERED_RANKS),
        other_cards=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        opponent_cards=st.lists(numbered_card_strategy, min_size=3, max_size=3),
        vault_size=st.integers(min_value=1, max_value=30),
    )
    @settings(max_examples=100)
    def test_diamond_disabled_does_not_trigger(
        self, diamond_rank: str, other_cards: list, opponent_cards: list,
        vault_size: int
    ) -> None:
        """When a Diamond card's ability is disabled, no vault manipulation
        should occur."""
        from src.entities.deck import Deck

        resolver = AbilityResolver(CombatSystem())
        diamond = Card(rank=diamond_rank, suit='Diamond')
        other_cards = [c for c in other_cards if c.suit != 'Diamond']
        assume(len(other_cards) == 2)
        opponent_cards = [c for c in opponent_cards if c.suit != 'Diamond']
        assume(len(opponent_cards) == 3)

        cards1 = [diamond] + other_cards

        p1 = make_player(1, vault_size=vault_size)
        p2 = make_player(2, vault_size=vault_size)
        draw_pile = Deck([])

        players = [p1, p2]
        cards = [cards1, opponent_cards]
        # Disable the Diamond card at index 0 for player 0
        disabled_abilities: dict = {0: [0]}

        total_vault_before = p1.vault.size() + p2.vault.size()

        resolver.execute_diamond_ability(players, cards, disabled_abilities, draw_pile)

        total_vault_after = p1.vault.size() + p2.vault.size()
        assert total_vault_after == total_vault_before, (
            f"Disabled Diamond should not remove cards. Before={total_vault_before}, after={total_vault_after}"
        )
        assert draw_pile.remaining() == 0, (
            "Disabled Diamond should not add cards to draw pile"
        )

    @given(
        face_rank=st.sampled_from(FACE_RANKS),
        other_cards=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        opponent_cards=st.lists(numbered_card_strategy, min_size=3, max_size=3),
        vault_size=st.integers(min_value=1, max_value=30),
    )
    @settings(max_examples=100)
    def test_diamond_face_card_does_not_trigger(
        self, face_rank: str, other_cards: list, opponent_cards: list,
        vault_size: int
    ) -> None:
        """Face cards with Diamond suit should NOT trigger the Diamond ability."""
        from src.entities.deck import Deck

        resolver = AbilityResolver(CombatSystem())
        face_diamond = Card(rank=face_rank, suit='Diamond')
        other_cards = [c for c in other_cards if c.suit != 'Diamond']
        assume(len(other_cards) == 2)
        opponent_cards = [c for c in opponent_cards if c.suit != 'Diamond']
        assume(len(opponent_cards) == 3)

        cards1 = [face_diamond] + other_cards

        p1 = make_player(1, vault_size=vault_size)
        p2 = make_player(2, vault_size=vault_size)
        draw_pile = Deck([])

        players = [p1, p2]
        cards = [cards1, opponent_cards]
        disabled_abilities: dict = {}

        total_vault_before = p1.vault.size() + p2.vault.size()

        resolver.execute_diamond_ability(players, cards, disabled_abilities, draw_pile)

        total_vault_after = p1.vault.size() + p2.vault.size()
        assert total_vault_after == total_vault_before, (
            f"Face Diamond should not trigger ability. Before={total_vault_before}, after={total_vault_after}"
        )
        assert draw_pile.remaining() == 0, (
            "Face Diamond should not add cards to draw pile"
        )


class TestHeartAbilityHealing:
    """**Validates: Requirements 8.1, 8.3, 17.4**

    Property 18: Heart Ability Healing
    For any numbered Heart card played by a round winner with any vault size,
    healing should equal floor(vault_size / 4), and final health should not
    exceed 50.
    """

    @given(
        heart_rank=st.sampled_from(NUMBERED_RANKS),
        other_cards=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        vault_size=st.integers(min_value=0, max_value=50),
        initial_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_heart_heals_by_floor_vault_div_4(
        self, heart_rank: str, other_cards: list, vault_size: int, initial_health: int
    ) -> None:
        """A numbered Heart card should heal the winner by floor(vault_size / 4)."""
        resolver = AbilityResolver(CombatSystem())
        heart_card = Card(rank=heart_rank, suit='Heart')
        winner_cards = [heart_card] + other_cards

        winner = make_player(1, vault_size=vault_size)
        winner.health = initial_health

        disabled_abilities: dict = {}
        winner_idx = 0

        resolver.execute_post_winner_abilities(winner, winner_cards, disabled_abilities, winner_idx)

        expected_heal = vault_size // 4
        # Count all numbered Heart cards in the hand (the explicit one + any from other_cards)
        heart_count = sum(1 for c in winner_cards if c.is_numbered_card() and c.suit == 'Heart')
        # Each Heart card heals independently, but heal() caps at 50
        expected_health = initial_health
        for _ in range(heart_count):
            expected_health = min(50, expected_health + expected_heal)

        assert winner.health == expected_health, (
            f"Heart healing should be floor({vault_size}/4)={expected_heal} per Heart card "
            f"({heart_count} Heart cards). Expected health={expected_health}, got {winner.health}"
        )

    @given(
        heart_rank=st.sampled_from(NUMBERED_RANKS),
        vault_size=st.integers(min_value=0, max_value=50),
        initial_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_heart_healing_does_not_exceed_50(
        self, heart_rank: str, vault_size: int, initial_health: int
    ) -> None:
        """After Heart healing, health should never exceed 50."""
        resolver = AbilityResolver(CombatSystem())
        heart_card = Card(rank=heart_rank, suit='Heart')
        # Use non-Heart cards to isolate a single Heart trigger
        winner_cards = [heart_card, Card(rank='2', suit='Club'), Card(rank='3', suit='Spade')]

        winner = make_player(1, vault_size=vault_size)
        winner.health = initial_health

        disabled_abilities: dict = {}
        winner_idx = 0

        resolver.execute_post_winner_abilities(winner, winner_cards, disabled_abilities, winner_idx)

        assert winner.health <= 50, (
            f"Health should never exceed 50 after healing. Got {winner.health}"
        )

        expected_heal = vault_size // 4
        expected_health = min(50, initial_health + expected_heal)
        assert winner.health == expected_health, (
            f"Expected health={expected_health} (initial={initial_health} + heal={expected_heal}, "
            f"capped at 50), got {winner.health}"
        )

    @given(
        heart_rank=st.sampled_from(NUMBERED_RANKS),
        vault_size=st.integers(min_value=0, max_value=50),
        initial_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_heart_disabled_does_not_heal(
        self, heart_rank: str, vault_size: int, initial_health: int
    ) -> None:
        """When a Heart card's ability is disabled, no healing should occur."""
        resolver = AbilityResolver(CombatSystem())
        heart_card = Card(rank=heart_rank, suit='Heart')
        winner_cards = [heart_card, Card(rank='2', suit='Club'), Card(rank='3', suit='Spade')]

        winner = make_player(1, vault_size=vault_size)
        winner.health = initial_health

        # Disable the Heart card at index 0 for the winner (player index 0)
        disabled_abilities: dict = {0: [0]}
        winner_idx = 0

        resolver.execute_post_winner_abilities(winner, winner_cards, disabled_abilities, winner_idx)

        assert winner.health == initial_health, (
            f"Disabled Heart should not heal. Expected health={initial_health}, got {winner.health}"
        )

    @given(
        face_rank=st.sampled_from(FACE_RANKS),
        vault_size=st.integers(min_value=4, max_value=50),
        initial_health=st.integers(min_value=1, max_value=40),
    )
    @settings(max_examples=100)
    def test_face_card_heart_suit_does_not_heal(
        self, face_rank: str, vault_size: int, initial_health: int
    ) -> None:
        """Face cards with Heart suit should NOT trigger the Heart healing ability."""
        resolver = AbilityResolver(CombatSystem())
        face_heart = Card(rank=face_rank, suit='Heart')
        winner_cards = [face_heart, Card(rank='2', suit='Club'), Card(rank='3', suit='Spade')]

        winner = make_player(1, vault_size=vault_size)
        winner.health = initial_health

        disabled_abilities: dict = {}
        winner_idx = 0

        resolver.execute_post_winner_abilities(winner, winner_cards, disabled_abilities, winner_idx)

        assert winner.health == initial_health, (
            f"Face Heart card should not trigger healing. "
            f"Expected health={initial_health}, got {winner.health}"
        )


class TestSuitAbilitiesOnlyOnNumberedCards:
    """**Validates: Requirements 6.2, 7.2, 8.2, 9.3**

    Property 15: Suit Abilities Only on Numbered Cards
    For any face card (Ace, Jack, Queen, King), suit abilities (Club, Spade,
    Heart, Diamond) should not activate regardless of the card's suit.
    """

    @given(
        face_rank=st.sampled_from(FACE_RANKS),
        suit=st.sampled_from(ALL_SUITS),
        other_numbered=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        opponent_cards=st.lists(numbered_card_strategy, min_size=3, max_size=3),
        vault_size=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_face_card_does_not_trigger_club_or_spade_bonus(
        self, face_rank: str, suit: str, other_numbered: list,
        opponent_cards: list, vault_size: int
    ) -> None:
        """Face cards should not produce damage or defense modifiers from suit
        abilities, even when their suit is Club or Spade."""
        # Ensure other cards are not Club/Spade to isolate the face card
        other_numbered = [
            Card(rank=c.rank, suit='Heart') for c in other_numbered
        ]
        opponent_cards = [
            Card(rank=c.rank, suit='Heart') for c in opponent_cards
        ]

        resolver = AbilityResolver(CombatSystem())
        face_card = Card(rank=face_rank, suit=suit)
        cards1 = [face_card] + other_numbered

        p1 = make_player(1, vault_size=vault_size)
        p1_initial_defense = p1.defense
        p2 = make_player(2, vault_size=0)

        players = [p1, p2]
        cards = [cards1, opponent_cards]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        # Face card should NOT have contributed any suit-based bonus
        # (damage_modifiers and defense_modifiers should be 0 for player 0
        #  since the only non-Heart card is the face card)
        assert damage_modifiers[0] == 0, (
            f"Face card {face_card} should not trigger Club damage bonus. "
            f"Got damage_modifiers[0]={damage_modifiers[0]}"
        )
        assert defense_modifiers[0] == 0, (
            f"Face card {face_card} should not trigger Spade defense bonus. "
            f"Got defense_modifiers[0]={defense_modifiers[0]}"
        )

    @given(
        face_rank=st.sampled_from(FACE_RANKS),
        vault_size=st.integers(min_value=4, max_value=50),
        initial_health=st.integers(min_value=1, max_value=40),
    )
    @settings(max_examples=100)
    def test_face_card_heart_suit_does_not_heal(
        self, face_rank: str, vault_size: int, initial_health: int
    ) -> None:
        """Face cards with Heart suit should NOT trigger healing via
        execute_post_winner_abilities."""
        resolver = AbilityResolver(CombatSystem())
        face_heart = Card(rank=face_rank, suit='Heart')
        winner_cards = [face_heart, Card(rank='2', suit='Club'), Card(rank='3', suit='Spade')]

        winner = make_player(1, vault_size=vault_size)
        winner.health = initial_health

        disabled_abilities: dict = {}
        winner_idx = 0

        resolver.execute_post_winner_abilities(winner, winner_cards, disabled_abilities, winner_idx)

        assert winner.health == initial_health, (
            f"Face card {face_heart} should not trigger Heart healing. "
            f"Expected health={initial_health}, got {winner.health}"
        )

    @given(
        face_rank=st.sampled_from(FACE_RANKS),
        other_numbered=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        opponent_cards=st.lists(numbered_card_strategy, min_size=3, max_size=3),
        vault_size=st.integers(min_value=1, max_value=30),
    )
    @settings(max_examples=100)
    def test_face_card_diamond_suit_does_not_manipulate_vault(
        self, face_rank: str, other_numbered: list, opponent_cards: list,
        vault_size: int
    ) -> None:
        """Face cards with Diamond suit should NOT trigger vault manipulation."""
        from src.entities.deck import Deck

        # Ensure other cards are NOT Diamond to isolate the face card
        other_numbered = [
            Card(rank=c.rank, suit='Club') for c in other_numbered
        ]
        opponent_cards = [
            Card(rank=c.rank, suit='Club') for c in opponent_cards
        ]

        resolver = AbilityResolver(CombatSystem())
        face_diamond = Card(rank=face_rank, suit='Diamond')
        cards1 = [face_diamond] + other_numbered

        p1 = make_player(1, vault_size=vault_size)
        p2 = make_player(2, vault_size=vault_size)
        draw_pile = Deck([])

        players = [p1, p2]
        cards = [cards1, opponent_cards]
        disabled_abilities: dict = {}

        total_vault_before = p1.vault.size() + p2.vault.size()

        resolver.execute_diamond_ability(players, cards, disabled_abilities, draw_pile)

        total_vault_after = p1.vault.size() + p2.vault.size()
        assert total_vault_after == total_vault_before, (
            f"Face Diamond card {face_diamond} should not trigger vault manipulation. "
            f"Vault total before={total_vault_before}, after={total_vault_after}"
        )
        assert draw_pile.remaining() == 0, (
            f"Face Diamond card should not add cards to draw pile. "
            f"Draw pile has {draw_pile.remaining()} cards"
        )

    @given(
        face_rank=st.sampled_from(FACE_RANKS),
        suit=st.sampled_from(ALL_SUITS),
    )
    @settings(max_examples=100)
    def test_face_card_get_suit_ability_returns_none(
        self, face_rank: str, suit: str
    ) -> None:
        """Card.get_suit_ability() should return None for all face cards."""
        card = Card(rank=face_rank, suit=suit)
        assert card.get_suit_ability() is None, (
            f"Face card {card} should return None from get_suit_ability(), "
            f"got {card.get_suit_ability()}"
        )


class TestAbilityExecutionOrder:
    """**Validates: Requirements 19.1-19.9**

    Property 40: Ability Execution Order
    For any round, abilities should execute in this exact order:
    (1) defense decay, (2) card shedding, (3) Ace, (4) Queen,
    (5) Jack & King, (6) Spade & Club, (7) score calculation,
    (8) Diamond, (9) Heart.
    """

    @given(
        ace_suit=st.sampled_from(ALL_SUITS),
        other_cards_p1=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        cards_p2=st.lists(numbered_card_strategy, min_size=3, max_size=3),
        vault_size=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=100)
    def test_pre_reveal_runs_before_post_reveal(
        self, ace_suit: str, other_cards_p1: list, cards_p2: list,
        vault_size: int
    ) -> None:
        """Ace (pre-reveal phase) should disable face cards before post-reveal
        abilities (Jack/King) execute. If an Ace is present, Jack and King
        abilities in the same round should be disabled."""
        resolver = AbilityResolver(CombatSystem())
        ace = Card(rank='A', suit=ace_suit)
        # Include a Jack in player 2's hand to verify it gets disabled
        cards_p2_with_jack = [Card(rank='J', suit='Club')] + cards_p2[:2]

        p1 = make_player(1, vault_size=vault_size)
        p2 = make_player(2, vault_size=vault_size)

        # Run the full resolve_abilities flow
        result = resolver.resolve_abilities(
            p1, p2,
            [ace] + other_cards_p1,
            cards_p2_with_jack
        )

        # Ace runs in pre-reveal, so Jack (index 0 of player 1's opponent)
        # should be in disabled_abilities
        assert 1 in result.disabled_abilities, (
            "Ace should disable face cards in pre-reveal phase before "
            "post-reveal abilities execute"
        )
        assert 0 in result.disabled_abilities[1], (
            "Jack at index 0 for player 2 should be disabled by Ace "
            "(pre-reveal runs before post-reveal)"
        )

    @given(
        queen_suit=st.sampled_from(ALL_SUITS),
        other_cards=st.lists(numbered_card_strategy, min_size=2, max_size=2),
        opponent_cards=st.lists(numbered_card_strategy, min_size=3, max_size=3),
        p1_vault=st.integers(min_value=0, max_value=20),
        p2_vault=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=100)
    def test_queen_disabling_applies_before_post_reveal(
        self, queen_suit: str, other_cards: list, opponent_cards: list,
        p1_vault: int, p2_vault: int
    ) -> None:
        """Queen (pre-reveal) should disable opponent abilities before
        post-reveal suit abilities (Spade/Club) execute. If Queen disables
        a Spade card, that card should not grant defense."""
        # Ensure no Aces in other cards (Ace overrides Queen)
        other_cards = [c for c in other_cards if c.rank != 'A']
        assume(len(other_cards) == 2)
        assume(all(c.rank != 'A' for c in opponent_cards))

        # Put a Spade numbered card at index 0 of opponent's hand
        spade_card = Card(rank='5', suit='Spade')
        opponent_hand = [spade_card] + opponent_cards[:2]

        resolver = AbilityResolver(CombatSystem())
        queen = Card(rank='Q', suit=queen_suit)
        cards1 = [queen] + other_cards

        p1 = make_player(1, vault_size=p1_vault)
        p2 = make_player(2, vault_size=p2_vault)
        p2_initial_defense = p2.defense

        players = [p1, p2]
        cards = [cards1, opponent_hand]
        disabled_abilities: dict = {}

        # Execute pre-reveal (Queen disables opponent cards)
        resolver.execute_pre_reveal_abilities(players, cards, disabled_abilities)

        # Queen should have disabled at least card index 0 of opponent
        assert 1 in disabled_abilities, (
            "Queen should disable at least one opponent ability"
        )
        assert 0 in disabled_abilities[1], (
            "Queen should disable opponent's first card (index 0)"
        )

        # Now execute post-reveal — the disabled Spade should NOT grant defense
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        # The Spade at index 0 was disabled by Queen, so its defense bonus
        # should not have been applied
        spade_bonus = p2_vault // 2
        # Count non-disabled Spade cards for player 2 (indices 1 and 2 only)
        non_disabled_spade_count = sum(
            1 for j, c in enumerate(opponent_hand)
            if j not in disabled_abilities.get(1, [])
            and c.is_numbered_card() and c.suit == 'Spade'
        )
        expected_defense_mod = spade_bonus * non_disabled_spade_count

        assert defense_modifiers[1] == expected_defense_mod, (
            f"Disabled Spade should not contribute defense. "
            f"Expected defense_modifiers[1]={expected_defense_mod}, "
            f"got {defense_modifiers[1]}"
        )

    @given(
        vault_size=st.integers(min_value=4, max_value=30),
        initial_health=st.integers(min_value=10, max_value=45),
    )
    @settings(max_examples=100)
    def test_heart_executes_after_winner_determination(
        self, vault_size: int, initial_health: int
    ) -> None:
        """Heart ability should only execute after the winner is decided
        (post-winner phase), not during pre-reveal or post-reveal phases.
        The resolve_abilities method should NOT trigger Heart healing."""
        resolver = AbilityResolver(CombatSystem())

        # Player 1 plays numbered Heart cards
        cards1 = [
            Card(rank='5', suit='Heart'),
            Card(rank='6', suit='Heart'),
            Card(rank='7', suit='Heart'),
        ]
        cards2 = [
            Card(rank='2', suit='Club'),
            Card(rank='3', suit='Club'),
            Card(rank='4', suit='Club'),
        ]

        p1 = make_player(1, vault_size=vault_size)
        p1.health = initial_health
        p2 = make_player(2, vault_size=0)

        # resolve_abilities handles pre-reveal + post-reveal + diamond,
        # but NOT Heart (post-winner). Health should be unchanged.
        resolver.resolve_abilities(p1, p2, cards1, cards2)

        assert p1.health == initial_health, (
            f"Heart should not activate during resolve_abilities (it's post-winner). "
            f"Expected health={initial_health}, got {p1.health}"
        )

    @given(
        vault_size=st.integers(min_value=2, max_value=30),
    )
    @settings(max_examples=100)
    def test_jack_king_execute_before_spade_club(
        self, vault_size: int
    ) -> None:
        """Jack & King (step 5) should execute before Spade & Club (step 6).
        King reduces opponent vault before Spade/Club use vault size for bonuses.
        After King reduces vault, Spade bonus should use the reduced vault size."""
        resolver = AbilityResolver(CombatSystem())

        # Player 1 plays King + numbered Spade
        # Player 2 plays numbered cards with a Spade
        cards1 = [
            Card(rank='K', suit='Club'),
            Card(rank='2', suit='Heart'),
            Card(rank='3', suit='Heart'),
        ]
        cards2 = [
            Card(rank='5', suit='Spade'),
            Card(rank='2', suit='Heart'),
            Card(rank='3', suit='Heart'),
        ]

        p1 = make_player(1, vault_size=0)
        p2 = make_player(2, vault_size=vault_size)
        p2_initial_defense = p2.defense

        players = [p1, p2]
        cards = [cards1, cards2]
        disabled_abilities: dict = {}
        damage_modifiers = {0: 0, 1: 0}
        defense_modifiers = {0: 0, 1: 0}

        resolver.execute_post_reveal_abilities(
            players, cards, disabled_abilities, damage_modifiers, defense_modifiers
        )

        # King reduces p2's vault by floor(vault_size / 4)
        vault_after_king = vault_size - (vault_size // 4)

        # Spade bonus for p2 should use the vault size AFTER King reduction
        expected_spade_bonus = vault_after_king // 2

        assert defense_modifiers[1] == expected_spade_bonus, (
            f"Spade bonus should use vault size after King reduction. "
            f"Original vault={vault_size}, after King={vault_after_king}, "
            f"expected Spade bonus={expected_spade_bonus}, "
            f"got defense_modifiers[1]={defense_modifiers[1]}"
        )
