"""Property-based tests for Player damage and defense mechanics.

Feature: card-game-core
- Property 27: Defense Blocks Standard Damage
- Property 30: True Damage Bypasses Defense
- Property 35: Healing Increases Health

Validates: Requirements 14.1, 14.2, 14.5, 17.2, 17.3, 17.4
"""

from hypothesis import given, settings
import hypothesis.strategies as st

from src.entities.player import Player


class TestDefenseBlocksStandardDamage:
    """**Validates: Requirements 14.1, 14.2**

    Property 27: For any player with defense D receiving standard damage S,
    if S <= D, health should not decrease and defense should become D - S;
    if S > D, defense should become 0 and health should decrease by S - D.
    """

    @given(
        defense=st.integers(min_value=0, max_value=200),
        standard_dmg=st.integers(min_value=0, max_value=200),
        initial_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_defense_absorbs_when_damage_lte_defense(
        self, defense: int, standard_dmg: int, initial_health: int
    ) -> None:
        """When standard damage <= defense, health stays the same and defense is reduced."""
        # Only test the case where damage <= defense
        if standard_dmg > defense:
            return

        player = Player(player_id=1, health=initial_health, defense=defense)
        player.take_damage(standard_dmg=standard_dmg, true_dmg=0)

        assert player.health == initial_health, (
            f"Health should not decrease when damage ({standard_dmg}) <= defense ({defense})"
        )
        assert player.defense == defense - standard_dmg, (
            f"Defense should be {defense - standard_dmg}, got {player.defense}"
        )

    @given(
        defense=st.integers(min_value=0, max_value=200),
        standard_dmg=st.integers(min_value=0, max_value=200),
        initial_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_damage_overflows_to_health_when_exceeds_defense(
        self, defense: int, standard_dmg: int, initial_health: int
    ) -> None:
        """When standard damage > defense, defense becomes 0 and health decreases by overflow."""
        # Only test the case where damage > defense
        if standard_dmg <= defense:
            return

        player = Player(player_id=1, health=initial_health, defense=defense)
        player.take_damage(standard_dmg=standard_dmg, true_dmg=0)

        overflow = standard_dmg - defense
        expected_health = max(0, initial_health - overflow)

        assert player.defense == 0, (
            f"Defense should be 0 when damage ({standard_dmg}) > defense ({defense})"
        )
        assert player.health == expected_health, (
            f"Health should be {expected_health}, got {player.health}"
        )


class TestTrueDamageBypassesDefense:
    """**Validates: Requirements 14.5**

    Property 30: For any player receiving true damage T, health should decrease
    by T regardless of defense value, and defense should remain unchanged.
    """

    @given(
        defense=st.integers(min_value=0, max_value=200),
        true_dmg=st.integers(min_value=0, max_value=100),
        initial_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_true_damage_reduces_health_ignoring_defense(
        self, defense: int, true_dmg: int, initial_health: int
    ) -> None:
        """True damage should reduce health directly, bypassing defense entirely."""
        player = Player(player_id=1, health=initial_health, defense=defense)
        player.take_damage(standard_dmg=0, true_dmg=true_dmg)

        expected_health = max(0, initial_health - true_dmg)

        assert player.health == expected_health, (
            f"Health should be {expected_health} after {true_dmg} true damage, got {player.health}"
        )
        assert player.defense == defense, (
            f"Defense should remain {defense} after true damage, got {player.defense}"
        )


class TestHealingIncreasesHealth:
    """**Validates: Requirements 17.3, 17.4**

    Property 35: For any player with health H receiving healing amount A,
    health should increase by A but not exceed 50.
    """

    @given(
        initial_health=st.integers(min_value=1, max_value=50),
        heal_amount=st.integers(min_value=0, max_value=100),
    )
    @settings(max_examples=100)
    def test_healing_increases_health_capped_at_50(
        self, initial_health: int, heal_amount: int
    ) -> None:
        """Healing should increase health by the given amount, but never exceed 50."""
        player = Player(player_id=1, health=initial_health)
        player.heal(heal_amount)

        expected_health = min(50, initial_health + heal_amount)

        assert player.health == expected_health, (
            f"Health should be {expected_health} after healing {heal_amount} from {initial_health}, "
            f"got {player.health}"
        )
        assert player.health <= 50, (
            f"Health should never exceed 50, got {player.health}"
        )


from src.entities.card import Card


# --- Strategies for card generation ---
_RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
_SUITS = ["Club", "Spade", "Heart", "Diamond"]

card_strategy = st.builds(Card, rank=st.sampled_from(_RANKS), suit=st.sampled_from(_SUITS))


class TestDefenseDecay:
    """**Validates: Requirements 14.3, 25.3**

    Property 28: For any player with defense D at the start of a round,
    defense should decrease by floor(D / 4) before card selection.
    """

    @given(
        defense=st.integers(min_value=0, max_value=500),
    )
    @settings(max_examples=100)
    def test_defense_decays_by_floor_quarter(self, defense: int) -> None:
        """Defense should decrease by floor(D / 4) after decay."""
        player = Player(player_id=1, health=50, defense=defense)
        expected_defense = defense - (defense // 4)

        player.decay_defense()

        assert player.defense == expected_defense, (
            f"Defense should be {expected_defense} after decaying from {defense}, "
            f"got {player.defense}"
        )

    @given(
        defense=st.integers(min_value=0, max_value=500),
    )
    @settings(max_examples=100)
    def test_defense_decay_uses_floor_division(self, defense: int) -> None:
        """The decay amount should always be floor(D / 4), never ceiling or rounding."""
        player = Player(player_id=1, health=50, defense=defense)
        decay_amount = defense // 4

        player.decay_defense()

        actual_decay = defense - player.defense
        assert actual_decay == decay_amount, (
            f"Decay amount should be {decay_amount} (floor({defense}/4)), "
            f"but actual decay was {actual_decay}"
        )

    @given(
        defense=st.integers(min_value=0, max_value=500),
        initial_health=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100)
    def test_defense_decay_does_not_affect_health(
        self, defense: int, initial_health: int
    ) -> None:
        """Defense decay should never change the player's health."""
        player = Player(player_id=1, health=initial_health, defense=defense)

        player.decay_defense()

        assert player.health == initial_health, (
            f"Health should remain {initial_health} after defense decay, got {player.health}"
        )


class TestCardSheddingMechanics:
    """**Validates: Requirements 16.1, 16.2, 16.3, 16.4**

    Property 33: For any player shedding N cards from their vault,
    N random cards should be removed from the vault and from the game,
    and the player should receive N benefits (each being +1 damage,
    +1 defense, or +1 health).

    Note: shed_card() only removes a card from the vault. The bonus
    is applied by the caller. Tests verify vault size decreases by 1
    per shed and that shedding on an empty vault is a no-op.
    """

    @given(
        vault_cards=st.lists(card_strategy, min_size=1, max_size=30),
    )
    @settings(max_examples=100)
    def test_shed_card_removes_one_card_from_vault(
        self, vault_cards: list,
    ) -> None:
        """Shedding a card should reduce vault size by exactly 1."""
        player = Player(player_id=1, health=50)
        player.vault.add_cards(vault_cards)
        initial_size = player.vault.size()

        player.shed_card("damage")

        assert player.vault.size() == initial_size - 1, (
            f"Vault size should be {initial_size - 1} after shedding, "
            f"got {player.vault.size()}"
        )

    @given(
        vault_cards=st.lists(card_strategy, min_size=1, max_size=20),
        n_sheds=st.integers(min_value=1, max_value=5),
        bonus_types=st.lists(
            st.sampled_from(["damage", "defense", "health"]),
            min_size=5,
            max_size=5,
        ),
    )
    @settings(max_examples=100)
    def test_shed_n_cards_removes_n_from_vault(
        self, vault_cards: list, n_sheds: int, bonus_types: list,
    ) -> None:
        """Shedding N cards should reduce vault size by N (capped at vault size)."""
        player = Player(player_id=1, health=50)
        player.vault.add_cards(vault_cards)
        initial_size = player.vault.size()
        actual_sheds = min(n_sheds, initial_size)

        for i in range(actual_sheds):
            player.shed_card(bonus_types[i])

        assert player.vault.size() == initial_size - actual_sheds, (
            f"Vault size should be {initial_size - actual_sheds} after shedding "
            f"{actual_sheds} cards, got {player.vault.size()}"
        )

    @given(
        bonus_type=st.sampled_from(["damage", "defense", "health"]),
    )
    @settings(max_examples=100)
    def test_shed_card_on_empty_vault_is_noop(self, bonus_type: str) -> None:
        """Shedding from an empty vault should not change anything."""
        player = Player(player_id=1, health=30, defense=5)
        initial_health = player.health
        initial_defense = player.defense

        player.shed_card(bonus_type)

        assert player.vault.size() == 0, (
            f"Vault should remain empty, got size {player.vault.size()}"
        )
        assert player.health == initial_health, (
            f"Health should remain {initial_health}, got {player.health}"
        )
        assert player.defense == initial_defense, (
            f"Defense should remain {initial_defense}, got {player.defense}"
        )
