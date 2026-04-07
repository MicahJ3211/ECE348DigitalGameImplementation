"""Unit tests for edge cases and specific examples.

Tests cover:
- Task 18.1: Card examples and face card suit ability exclusion
- Task 18.2: Empty vault edge cases
- Task 18.3: Zero defense edge case
- Task 18.4: Maximum health edge case
- Task 18.5: Insufficient cards edge case
- Task 18.6: Asset loading failures
"""

import pytest
from unittest.mock import patch, MagicMock

from src.entities.card import Card
from src.entities.player import Player
from src.entities.vault import Vault
from src.entities.deck import Deck
from src.systems.combat_system import CombatSystem
from src.systems.ability_resolver import AbilityResolver


# ---------------------------------------------------------------------------
# Task 18.1: Card examples and face card suit ability exclusion
# Validates: Requirements 5.1, 5.2, 5.3, 6.2, 7.2, 8.2, 9.3
# ---------------------------------------------------------------------------

class TestCardExamples:
    """Test specific card instances for base damage and ability behavior."""

    def test_ace_of_clubs_base_damage(self):
        """Ace of Clubs should have base damage of 1."""
        card = Card(rank='A', suit='Club')
        assert card.get_base_damage() == 1

    def test_ten_of_hearts_base_damage(self):
        """10 of Hearts should have base damage of 10."""
        card = Card(rank='10', suit='Heart')
        assert card.get_base_damage() == 10

    def test_king_of_spades_base_damage(self):
        """King of Spades should have base damage of 10."""
        card = Card(rank='K', suit='Spade')
        assert card.get_base_damage() == 10

    def test_ace_is_face_card(self):
        """Ace should be classified as a face card."""
        card = Card(rank='A', suit='Club')
        assert card.is_face_card() is True
        assert card.is_numbered_card() is False

    def test_ten_is_numbered_card(self):
        """10 should be classified as a numbered card."""
        card = Card(rank='10', suit='Heart')
        assert card.is_face_card() is False
        assert card.is_numbered_card() is True

    def test_king_is_face_card(self):
        """King should be classified as a face card."""
        card = Card(rank='K', suit='Spade')
        assert card.is_face_card() is True
        assert card.is_numbered_card() is False


class TestFaceCardSuitAbilityExclusion:
    """Face cards should NOT trigger suit abilities. Validates: 6.2, 7.2, 8.2, 9.3."""

    def test_jack_of_clubs_no_suit_ability(self):
        """Jack of Clubs should not trigger Club suit ability."""
        card = Card(rank='J', suit='Club')
        assert card.get_suit_ability() is None

    def test_queen_of_spades_no_suit_ability(self):
        """Queen of Spades should not trigger Spade suit ability."""
        card = Card(rank='Q', suit='Spade')
        assert card.get_suit_ability() is None

    def test_king_of_hearts_no_suit_ability(self):
        """King of Hearts should not trigger Heart suit ability."""
        card = Card(rank='K', suit='Heart')
        assert card.get_suit_ability() is None

    def test_ace_of_diamonds_no_suit_ability(self):
        """Ace of Diamonds should not trigger Diamond suit ability."""
        card = Card(rank='A', suit='Diamond')
        assert card.get_suit_ability() is None

    def test_numbered_club_has_suit_ability(self):
        """Numbered Club card should trigger Club suit ability."""
        card = Card(rank='5', suit='Club')
        assert card.get_suit_ability() == 'Club'

    def test_numbered_spade_has_suit_ability(self):
        """Numbered Spade card should trigger Spade suit ability."""
        card = Card(rank='7', suit='Spade')
        assert card.get_suit_ability() == 'Spade'

    def test_numbered_heart_has_suit_ability(self):
        """Numbered Heart card should trigger Heart suit ability."""
        card = Card(rank='3', suit='Heart')
        assert card.get_suit_ability() == 'Heart'

    def test_numbered_diamond_has_suit_ability(self):
        """Numbered Diamond card should trigger Diamond suit ability."""
        card = Card(rank='9', suit='Diamond')
        assert card.get_suit_ability() == 'Diamond'

    def test_face_cards_have_face_ability(self):
        """Face cards should return their face ability instead."""
        assert Card(rank='A', suit='Club').get_face_ability() == 'A'
        assert Card(rank='J', suit='Spade').get_face_ability() == 'J'
        assert Card(rank='Q', suit='Heart').get_face_ability() == 'Q'
        assert Card(rank='K', suit='Diamond').get_face_ability() == 'K'

    def test_numbered_cards_no_face_ability(self):
        """Numbered cards should not have face abilities."""
        card = Card(rank='5', suit='Club')
        assert card.get_face_ability() is None


# ---------------------------------------------------------------------------
# Task 18.2: Empty vault edge cases
# Validates: Requirements 6.1, 7.1, 8.1, 9.1
# ---------------------------------------------------------------------------

class TestEmptyVaultEdgeCases:
    """Test abilities when vaults are empty (bonus should be 0)."""

    def test_club_ability_empty_vault_bonus_is_zero(self):
        """Club ability with empty vault: damage bonus = floor(0 / 2) = 0."""
        player = Player(player_id=1)
        assert player.vault.is_empty()
        # Club bonus = floor(vault_size / 2) = floor(0 / 2) = 0
        bonus = player.vault.size() // 2
        assert bonus == 0

    def test_spade_ability_empty_vault_bonus_is_zero(self):
        """Spade ability with empty vault: defense bonus = floor(0 / 2) = 0."""
        player = Player(player_id=1)
        assert player.vault.is_empty()
        # Spade bonus = floor(vault_size / 2) = floor(0 / 2) = 0
        bonus = player.vault.size() // 2
        assert bonus == 0

    def test_heart_ability_empty_vault_heal_is_zero(self):
        """Heart ability with empty vault: heal = floor(0 / 4) = 0."""
        player = Player(player_id=1, health=30)
        assert player.vault.is_empty()
        # Heart heal = floor(vault_size / 4) = floor(0 / 4) = 0
        heal_amount = player.vault.size() // 4
        assert heal_amount == 0
        player.heal(heal_amount)
        assert player.health == 30  # No change

    def test_diamond_ability_both_vaults_empty_skips(self):
        """Diamond ability with both vaults empty should skip (no crash)."""
        player1 = Player(player_id=1)
        player2 = Player(player_id=2)
        draw_pile = Deck([])

        assert player1.vault.is_empty()
        assert player2.vault.is_empty()

        resolver = AbilityResolver(CombatSystem())
        # Play a numbered Diamond card for player1, filler cards for rest
        cards1 = [Card(rank='5', suit='Diamond'), Card(rank='2', suit='Club'), Card(rank='3', suit='Club')]
        cards2 = [Card(rank='4', suit='Club'), Card(rank='6', suit='Club'), Card(rank='7', suit='Club')]

        # Execute diamond ability - should not crash with empty vaults
        resolver.execute_diamond_ability([player1, player2], [cards1, cards2], {}, draw_pile)

        # Vaults should still be empty, draw pile should still be empty
        assert player1.vault.is_empty()
        assert player2.vault.is_empty()
        assert draw_pile.remaining() == 0

    def test_club_ability_resolver_empty_vault(self):
        """AbilityResolver should add 0 damage bonus for Club with empty vault."""
        player1 = Player(player_id=1)
        player2 = Player(player_id=2)
        combat = CombatSystem()
        resolver = AbilityResolver(combat)

        # Player 1 plays a numbered Club card
        cards1 = [Card(rank='5', suit='Club'), Card(rank='2', suit='Heart'), Card(rank='3', suit='Heart')]
        cards2 = [Card(rank='4', suit='Heart'), Card(rank='6', suit='Heart'), Card(rank='7', suit='Heart')]

        damage_mods = {0: 0, 1: 0}
        defense_mods = {0: 0, 1: 0}
        disabled = {}

        resolver.execute_post_reveal_abilities(
            [player1, player2], [cards1, cards2], disabled, damage_mods, defense_mods
        )

        # With empty vault, Club bonus = floor(0/2) = 0
        assert damage_mods[0] == 0

    def test_spade_ability_resolver_empty_vault(self):
        """AbilityResolver should add 0 defense bonus for Spade with empty vault."""
        player1 = Player(player_id=1)
        player2 = Player(player_id=2)
        combat = CombatSystem()
        resolver = AbilityResolver(combat)

        cards1 = [Card(rank='5', suit='Spade'), Card(rank='2', suit='Heart'), Card(rank='3', suit='Heart')]
        cards2 = [Card(rank='4', suit='Heart'), Card(rank='6', suit='Heart'), Card(rank='7', suit='Heart')]

        damage_mods = {0: 0, 1: 0}
        defense_mods = {0: 0, 1: 0}
        disabled = {}

        resolver.execute_post_reveal_abilities(
            [player1, player2], [cards1, cards2], disabled, damage_mods, defense_mods
        )

        # With empty vault, Spade bonus = floor(0/2) = 0
        assert defense_mods[0] == 0
        assert player1.defense == 0

    def test_heart_ability_resolver_empty_vault(self):
        """AbilityResolver should heal 0 for Heart with empty vault."""
        player1 = Player(player_id=1, health=30)
        resolver = AbilityResolver(CombatSystem())

        cards = [Card(rank='5', suit='Heart'), Card(rank='2', suit='Club'), Card(rank='3', suit='Club')]

        resolver.execute_post_winner_abilities(player1, cards, {}, winner_idx=0)

        # With empty vault, Heart heal = floor(0/4) = 0
        assert player1.health == 30


# ---------------------------------------------------------------------------
# Task 18.3: Zero defense edge case
# Validates: Requirements 14.1, 14.2
# ---------------------------------------------------------------------------

class TestZeroDefenseEdgeCase:
    """Test damage application when defense is 0 (full damage to health)."""

    def test_standard_damage_with_zero_defense_reduces_health(self):
        """With defense=0, all standard damage goes directly to health."""
        player = Player(player_id=1, health=50, defense=0)
        player.take_damage(standard_dmg=15, true_dmg=0)
        assert player.health == 35
        assert player.defense == 0

    def test_true_damage_with_zero_defense_reduces_health(self):
        """True damage bypasses defense regardless, health reduced directly."""
        player = Player(player_id=1, health=50, defense=0)
        player.take_damage(standard_dmg=0, true_dmg=10)
        assert player.health == 40
        assert player.defense == 0

    def test_combined_damage_with_zero_defense(self):
        """Both standard and true damage reduce health when defense=0."""
        player = Player(player_id=1, health=50, defense=0)
        player.take_damage(standard_dmg=10, true_dmg=5)
        assert player.health == 35
        assert player.defense == 0

    def test_lethal_damage_with_zero_defense(self):
        """Damage exceeding health should set health to 0, not negative."""
        player = Player(player_id=1, health=10, defense=0)
        player.take_damage(standard_dmg=20, true_dmg=0)
        assert player.health == 0

    def test_combat_system_apply_damage_zero_defense(self):
        """CombatSystem.apply_damage with defense=0 should reduce health fully."""
        player = Player(player_id=1, health=50, defense=0)
        combat = CombatSystem()
        combat.apply_damage(player, standard_dmg=20, true_dmg=0)
        assert player.health == 30
        assert player.defense == 0


# ---------------------------------------------------------------------------
# Task 18.4: Maximum health edge case
# Validates: Requirements 17.4
# ---------------------------------------------------------------------------

class TestMaximumHealthEdgeCase:
    """Test healing when health is at or near maximum (50)."""

    def test_heal_at_max_health_stays_at_50(self):
        """Healing when health=50 should keep health at 50."""
        player = Player(player_id=1, health=50)
        player.heal(10)
        assert player.health == 50

    def test_heal_near_max_caps_at_50(self):
        """Healing that would exceed 50 should cap at 50."""
        player = Player(player_id=1, health=48)
        player.heal(5)
        assert player.health == 50

    def test_heal_to_exactly_50(self):
        """Healing that brings health exactly to 50 should work."""
        player = Player(player_id=1, health=45)
        player.heal(5)
        assert player.health == 50

    def test_heart_ability_at_max_health(self):
        """Heart ability should not exceed 50 health even with large vault."""
        player = Player(player_id=1, health=50)
        # Add cards to vault so heal amount > 0
        filler_cards = [Card(rank=str(i), suit='Club') for i in range(2, 10)]
        player.vault.add_cards(filler_cards)  # 8 cards, heal = floor(8/4) = 2

        resolver = AbilityResolver(CombatSystem())
        cards = [Card(rank='5', suit='Heart'), Card(rank='2', suit='Club'), Card(rank='3', suit='Club')]

        resolver.execute_post_winner_abilities(player, cards, {}, winner_idx=0)

        assert player.health == 50


# ---------------------------------------------------------------------------
# Task 18.5: Insufficient cards edge case
# Validates: Requirements 18.4, 24.4
# ---------------------------------------------------------------------------

class TestInsufficientCardsEdgeCase:
    """Test game end when draw pile cannot provide 3 cards per player."""

    def test_game_ends_when_deck_empty_and_hands_empty(self):
        """Game should end when deck is empty and players have no cards."""
        player1 = Player(player_id=1, health=50)
        player2 = Player(player_id=2, health=50)
        player1.deck = Deck([])
        player2.deck = Deck([])
        player1.hand = []
        player2.hand = []

        # Give player1 more vault cards to be the winner
        player1.vault.add_cards([Card(rank='2', suit='Club'), Card(rank='3', suit='Club')])

        combat = CombatSystem()
        result = combat.check_win_condition(player1, player2)

        assert result.game_over is True
        assert result.winner_id == 1
        assert result.reason == 'vault'

    def test_game_ends_when_deck_has_fewer_than_3_cards(self):
        """Game should end when deck can't provide enough cards for a full round."""
        player1 = Player(player_id=1, health=50)
        player2 = Player(player_id=2, health=50)
        # Only 2 cards in deck, 0 in hand - can't play 3 cards
        player1.deck = Deck([Card(rank='2', suit='Club'), Card(rank='3', suit='Club')])
        player2.deck = Deck([Card(rank='4', suit='Club'), Card(rank='5', suit='Club')])
        player1.hand = []
        player2.hand = []

        # Player2 has more vault cards
        player2.vault.add_cards([Card(rank='6', suit='Club'), Card(rank='7', suit='Club'), Card(rank='8', suit='Club')])

        combat = CombatSystem()
        result = combat.check_win_condition(player1, player2)

        assert result.game_over is True
        assert result.winner_id == 2
        assert result.reason == 'vault'

    def test_game_ends_tie_when_equal_vaults(self):
        """Game should end in tie when both players have equal vault sizes."""
        player1 = Player(player_id=1, health=50)
        player2 = Player(player_id=2, health=50)
        player1.deck = Deck([])
        player2.deck = Deck([])
        player1.hand = []
        player2.hand = []

        # Equal vault sizes
        player1.vault.add_cards([Card(rank='2', suit='Club')])
        player2.vault.add_cards([Card(rank='3', suit='Club')])

        combat = CombatSystem()
        result = combat.check_win_condition(player1, player2)

        assert result.game_over is True
        assert result.winner_id is None
        assert result.reason == 'tie'

    def test_game_continues_when_enough_cards(self):
        """Game should not end when players have enough cards to play."""
        player1 = Player(player_id=1, health=50)
        player2 = Player(player_id=2, health=50)
        cards = [Card(rank=str(i), suit='Club') for i in range(2, 8)]
        player1.deck = Deck(cards[:3])
        player2.deck = Deck(cards[3:])
        player1.hand = []
        player2.hand = []

        combat = CombatSystem()
        result = combat.check_win_condition(player1, player2)

        assert result.game_over is False

    def test_game_continues_when_hand_has_enough_cards(self):
        """Game should continue if hand already has 3+ cards even with empty deck."""
        player1 = Player(player_id=1, health=50)
        player2 = Player(player_id=2, health=50)
        player1.deck = Deck([])
        player2.deck = Deck([])
        player1.hand = [Card(rank='2', suit='Club'), Card(rank='3', suit='Club'), Card(rank='4', suit='Club')]
        player2.hand = [Card(rank='5', suit='Club'), Card(rank='6', suit='Club'), Card(rank='7', suit='Club')]

        combat = CombatSystem()
        result = combat.check_win_condition(player1, player2)

        assert result.game_over is False


# ---------------------------------------------------------------------------
# Task 18.6: Asset loading failures
# Validates: Requirements 1.5
# ---------------------------------------------------------------------------

class TestAssetLoadingFailures:
    """Test graceful degradation with missing images and fallback fonts."""

    @patch('pygame.font.Font', side_effect=Exception("Font not found"))
    @patch('pygame.font.SysFont')
    @patch('pygame.Surface')
    @patch('pygame.time.Clock')
    def test_fallback_fonts_on_font_load_failure(self, mock_clock, mock_surface, mock_sysfont, mock_font):
        """When primary font loading fails, system fonts should be used as fallback."""
        mock_sysfont.return_value = MagicMock()
        mock_clock_instance = MagicMock()
        mock_clock.return_value = mock_clock_instance

        # Import Game and test load_assets
        from src.game import Game

        with patch.object(Game, 'setup_scenes'):
            game = Game(mock_surface)

        # SysFont should have been called as fallback
        assert mock_sysfont.called

    @patch('pygame.font.Font')
    @patch('os.path.exists', return_value=False)
    @patch('pygame.Surface')
    @patch('pygame.time.Clock')
    def test_missing_images_returns_true(self, mock_clock, mock_surface, mock_exists, mock_font):
        """When image directory doesn't exist, load_assets should still return True."""
        mock_font.return_value = MagicMock()
        mock_clock_instance = MagicMock()
        mock_clock.return_value = mock_clock_instance

        from src.game import Game

        with patch.object(Game, 'setup_scenes'):
            game = Game(mock_surface)

        # load_assets is called in __init__, test it directly
        result = game.load_assets()
        assert result is True

    @patch('pygame.font.Font', side_effect=Exception("Font not found"))
    @patch('pygame.font.SysFont', side_effect=Exception("No system fonts"))
    @patch('pygame.Surface')
    @patch('pygame.time.Clock')
    def test_all_fonts_fail_returns_false(self, mock_clock, mock_surface, mock_sysfont, mock_font):
        """When all font loading fails, load_assets should return False."""
        mock_clock_instance = MagicMock()
        mock_clock.return_value = mock_clock_instance

        from src.game import Game

        with patch.object(Game, 'setup_scenes'):
            game = Game(mock_surface)

        result = game.load_assets()
        assert result is False
