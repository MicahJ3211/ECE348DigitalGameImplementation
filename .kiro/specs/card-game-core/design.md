# Design Document: Card Game Core

## Overview

This design document specifies the architecture and implementation approach for a strategic two-player card game built with Python and pygame. The game features simultaneous card play, complex ability resolution, and resource management through a vault system.

### System Goals

- Provide a smooth 60 FPS gameplay experience with responsive mouse input
- Implement complex card interactions with strict order of operations
- Manage game state across multiple scenes (menu, deck building, gameplay, game over)
- Ensure accurate combat resolution with multiple damage types and abilities
- Display clear visual feedback for all game state changes

### Technical Constraints

- Python 3.8+ with pygame library
- 1280x720 window resolution
- 60 FPS target frame rate
- Mouse-based input only
- Turn-based state management
- All rounding uses floor function (round down)

## Architecture

### High-Level Architecture

The system follows a component-based architecture with clear separation between game logic, rendering, and input handling:

```
┌─────────────────────────────────────────────────────────────┐
│                        Game_Engine                          │
│  (Main loop, pygame initialization, frame rate control)    │
└────────────┬────────────────────────────────────┬───────────┘
             │                                    │
    ┌────────▼────────┐                  ┌───────▼────────┐
    │ Scene_Manager   │                  │ Input_Handler  │
    │ (State machine) │                  │ (Mouse events) │
    └────────┬────────┘                  └───────┬────────┘
             │                                    │
    ┌────────▼────────────────────────────────────▼────────┐
    │                  Active Scene                        │
    │  (MenuScene / DeckBuilderScene / GameplayScene /     │
    │   GameOverScene)                                     │
    └────────┬─────────────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────────────┐
    │              Game Systems (Gameplay Scene)          │
    │  ┌──────────────┐  ┌──────────────┐                │
    │  │Combat_System │  │Ability_      │                │
    │  │              │  │Resolver      │                │
    │  └──────────────┘  └──────────────┘                │
    │  ┌──────────────┐  ┌──────────────┐                │
    │  │UI_Manager    │  │Deck_Builder  │                │
    │  └──────────────┘  └──────────────┘                │
    └────────┬────────────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────────────┐
    │                   Entities                          │
    │  Card, Player, Vault, Deck                          │
    └─────────────────────────────────────────────────────┘
```

### Design Patterns

**State Pattern**: Scene_Manager uses state pattern to manage transitions between menu, deck building, gameplay, and game over scenes.

**Component Pattern**: Entities (Player, Card) are composed of data and behavior, with systems (Combat_System, Ability_Resolver) operating on them.

**Observer Pattern**: UI_Manager observes game state changes to update displays.

**Command Pattern**: Card abilities are implemented as commands that execute in a specific order.

## Components and Interfaces

### Game_Engine

**Responsibility**: Initialize pygame, manage main game loop, control frame rate, coordinate scene rendering.

**Interface**:
```python
class GameEngine:
    def __init__(self, width: int, height: int, fps: int)
    def run() -> None
    def load_assets() -> bool
    def handle_events() -> None
    def update(delta_time: float) -> None
    def render() -> None
    def quit() -> None
```

**Key Behaviors**:
- Initialize pygame with 1280x720 window
- Maintain 60 FPS using pygame.time.Clock
- Load assets before gameplay (images, sounds, fonts)
- Delegate event handling to Input_Handler
- Delegate updates and rendering to Scene_Manager
- Handle window close events gracefully

### Scene_Manager

**Responsibility**: Manage scene transitions and lifecycle, maintain current scene state.

**Interface**:
```python
class SceneManager:
    def __init__(self, engine: GameEngine)
    def change_scene(scene_name: str, **kwargs) -> None
    def update(delta_time: float) -> None
    def render(screen: pygame.Surface) -> None
    def handle_input(event: pygame.event.Event) -> None
```

**Scenes**:
- **MenuScene**: Display start game and exit options
- **DeckBuilderScene**: Allow players to select 26 cards each
- **GameplayScene**: Main game loop with rounds and combat
- **GameOverScene**: Display winner and return to menu option

### Input_Handler

**Responsibility**: Process mouse events, validate input, provide feedback for selections.

**Interface**:
```python
class InputHandler:
    def handle_event(event: pygame.event.Event, scene: Scene) -> None
    def get_hovered_card(mouse_pos: tuple[int, int], cards: list[Card]) -> Card | None
    def is_valid_selection(selected_cards: list[Card], hand: list[Card]) -> bool
```

**Key Behaviors**:
- Track mouse position and clicks
- Detect card hover and selection
- Validate selection count (exactly 3 cards)
- Prevent interaction during animations
- Provide visual feedback for selections

### Deck_Builder

**Responsibility**: Manage deck construction phase, validate card selections, shuffle and deal initial hands.

**Interface**:
```python
class DeckBuilder:
    def __init__(self)
    def select_card(player_id: int, card: Card) -> bool
    def is_selection_complete() -> bool
    def create_game_deck() -> Deck
    def deal_initial_hands(deck: Deck, players: list[Player]) -> None
```

**Key Behaviors**:
- Track each player's 26 card selections
- Prevent duplicate selections
- Combine selections into 52-card deck
- Shuffle deck before dealing
- Deal 6 cards to each player

### Combat_System

**Responsibility**: Resolve rounds, calculate damage, determine winners, manage health/defense/vault.

**Interface**:
```python
class CombatSystem:
    def __init__(self)
    def resolve_round(player1: Player, player2: Player, 
                     cards1: list[Card], cards2: list[Card]) -> RoundResult
    def calculate_base_damage(cards: list[Card]) -> int
    def apply_damage(player: Player, standard_dmg: int, true_dmg: int) -> None
    def determine_winner(p1_damage: int, p2_damage: int, jack_count: int) -> int
    def add_to_vault(player: Player, cards: list[Card]) -> None
    def check_win_condition(player1: Player, player2: Player) -> WinCondition
```

**Key Behaviors**:
- Calculate base damage from card ranks
- Apply standard damage (blocked by defense)
- Apply true damage (bypasses defense)
- Determine round winner based on net standard damage
- Handle tied rounds (shuffle cards back)
- Award cards to winner's vault
- Check health and vault win conditions
- Manage defense decay (1/4 per round)

### Ability_Resolver

**Responsibility**: Execute card abilities in correct order, handle ability interactions.

**Interface**:
```python
class AbilityResolver:
    def __init__(self, combat_system: CombatSystem)
    def resolve_abilities(player1: Player, player2: Player,
                         cards1: list[Card], cards2: list[Card]) -> AbilityResult
    def execute_pre_reveal_abilities(players: list[Player], cards: list[list[Card]]) -> None
    def execute_post_reveal_abilities(players: list[Player], cards: list[list[Card]]) -> None
    def execute_post_winner_abilities(winner: Player, cards: list[Card]) -> None
```

**Order of Operations**:
1. **Before Reveal**: Defense decay → Card shedding → Ace → Queen
2. **After Reveal**: Jack & King → Spade & Club → Score calculation → Diamond
3. **After Winner**: Heart

**Ability Implementations**:
- **Club** (numbered): +damage = floor(vault_size / 2)
- **Spade** (numbered): +defense = floor(vault_size / 2)
- **Heart** (numbered, winner only): +health = floor(vault_size / 4), capped at 50
- **Diamond** (numbered): Remove random card from any vault to draw pile
- **Ace**: Disable all face card abilities
- **Jack**: Reverse round logic (lower wins), multiple Jacks flip repeatedly
- **Queen**: Disable opponent abilities (2 if smaller vault, 1 otherwise)
- **King**: True damage = opponent vault size, remove floor(vault_size / 4) cards from game

### UI_Manager

**Responsibility**: Render game state, display cards, show player stats, provide visual feedback.

**Interface**:
```python
class UIManager:
    def __init__(self, screen: pygame.Surface)
    def render_player_stats(player: Player, position: str) -> None
    def render_hand(cards: list[Card], selected: list[Card]) -> None
    def render_played_cards(cards: list[Card], revealed: bool) -> None
    def render_round_info(round_num: int, phase: str) -> None
    def show_ability_animation(ability: str, target: Player) -> None
```

**Display Elements**:
- Player health bars (top and bottom)
- Defense values (shield icon + number)
- Vault sizes (card stack icon + number)
- Hand cards (bottom for player, top for opponent)
- Played cards (center area, face down then revealed)
- Round number and phase indicator
- Ability activation animations

## Data Models

### Card

```python
@dataclass
class Card:
    rank: str  # 'A', '2'-'10', 'J', 'Q', 'K'
    suit: str  # 'Club', 'Spade', 'Heart', 'Diamond'
    
    def get_base_damage(self) -> int:
        """Returns base damage: Ace=1, 2-10=rank, Face=10"""
        
    def is_face_card(self) -> bool:
        """Returns True if rank is J, Q, K, or A"""
        
    def is_numbered_card(self) -> bool:
        """Returns True if rank is 2-10"""
        
    def get_suit_ability(self) -> str | None:
        """Returns suit ability name if numbered card, None if face"""
        
    def get_face_ability(self) -> str | None:
        """Returns face ability name if face card, None otherwise"""
```

### Player

```python
@dataclass
class Player:
    player_id: int
    health: int  # Starting: 50
    defense: int  # Starting: 0
    vault: Vault
    hand: list[Card]
    deck: Deck
    
    def take_damage(self, standard_dmg: int, true_dmg: int) -> None:
        """Apply damage, defense blocks standard damage first"""
        
    def heal(self, amount: int) -> None:
        """Increase health, capped at 50"""
        
    def add_defense(self, amount: int) -> None:
        """Increase defense value"""
        
    def decay_defense(self) -> None:
        """Reduce defense by floor(defense / 4)"""
        
    def draw_cards(self, count: int) -> None:
        """Draw cards from deck to hand"""
        
    def shed_card(self, bonus_type: str) -> None:
        """Remove random vault card, apply bonus (+1 dmg/def/hp)"""
```

### Vault

```python
class Vault:
    def __init__(self):
        self._cards: list[Card] = []
        
    def add_cards(self, cards: list[Card]) -> None:
        """Add cards to vault"""
        
    def remove_random_card(self) -> Card | None:
        """Remove and return random card, or None if empty"""
        
    def remove_cards_from_game(self, count: int) -> list[Card]:
        """Remove count cards permanently (King ability)"""
        
    def size(self) -> int:
        """Return number of cards in vault"""
        
    def is_empty(self) -> bool:
        """Return True if vault has no cards"""
```

### Deck

```python
class Deck:
    def __init__(self, cards: list[Card]):
        self._cards: list[Card] = cards
        
    def shuffle(self) -> None:
        """Randomize card order"""
        
    def draw(self, count: int) -> list[Card]:
        """Remove and return top count cards"""
        
    def add_cards(self, cards: list[Card]) -> None:
        """Add cards to bottom of deck (for tied rounds)"""
        
    def remaining(self) -> int:
        """Return number of cards left"""
        
    def can_draw(self, count: int) -> bool:
        """Return True if count cards available"""
```

### RoundResult

```python
@dataclass
class RoundResult:
    winner_id: int | None  # None for tie
    p1_standard_damage: int
    p2_standard_damage: int
    p1_true_damage: int
    p2_true_damage: int
    played_cards: list[Card]  # All 6 cards
    abilities_activated: list[str]  # Log of abilities
```

### AbilityResult

```python
@dataclass
class AbilityResult:
    damage_modifiers: dict[int, int]  # player_id -> damage bonus
    defense_modifiers: dict[int, int]  # player_id -> defense bonus
    disabled_abilities: dict[int, list[int]]  # player_id -> card indices
    jack_count: int  # Number of Jacks played
    king_activated: bool
```

### WinCondition

```python
@dataclass
class WinCondition:
    game_over: bool
    winner_id: int | None  # None for tie
    reason: str  # 'health', 'vault', 'tie'
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Base Damage Calculation

*For any* card, the base damage should be: 1 for Ace, the rank number for numbered cards (2-10), and 10 for face cards (Jack, Queen, King).

**Validates: Requirements 5.1, 5.2, 5.3**

### Property 2: Damage Summation

*For any* set of 3 cards played by a player, the total base damage should equal the sum of individual card base damages.

**Validates: Requirements 5.4**

### Property 3: Duplicate Card Prevention

*For any* card in the deck, if one player selects it during deck building, the other player should not be able to select the same card.

**Validates: Requirements 2.2**

### Property 4: Deck Combination

*For any* two valid 26-card selections from different players, combining them should produce exactly one 52-card game deck containing all selected cards.

**Validates: Requirements 2.3**

### Property 5: Deck Shuffling

*For any* combined 52-card deck, after shuffling, the card order should be randomized (with high probability of being different from the original order).

**Validates: Requirements 2.4**

### Property 6: Initial Hand Dealing

*For any* shuffled deck, dealing initial hands should give each player exactly 6 cards and reduce the deck by 12 cards.

**Validates: Requirements 2.5**

### Property 7: Card Selection Limit

*For any* player hand, attempting to select more than 3 cards should be prevented, and only selections of exactly 3 cards should allow confirmation.

**Validates: Requirements 3.1, 22.1, 22.3**

### Property 8: Selection Reversibility

*For any* selected card before confirmation, clicking it again should deselect it and remove it from the selection.

**Validates: Requirements 3.3**

### Property 9: Selection Lock After Confirmation

*For any* confirmed card selection, attempts to modify the selection should be rejected until the round completes.

**Validates: Requirements 3.6**

### Property 10: Simultaneous Reveal

*For any* game state where both players have confirmed their selections, all 6 cards should be revealed simultaneously.

**Validates: Requirements 4.1**

### Property 11: Round Winner Determination

*For any* two players' net standard damage values (after cancellation), the player with higher damage should win the round, unless Jack abilities reverse the logic.

**Validates: Requirements 4.4**

### Property 12: Vault Addition on Win

*For any* round with a winner, all 6 played cards should be added to the winner's vault, increasing vault size by 6.

**Validates: Requirements 4.5, 18.1**

### Property 13: Tied Round Handling

*For any* round where both players deal equal net standard damage, all 6 played cards should be shuffled back into the draw pile.

**Validates: Requirements 4.6**

### Property 14: Post-Round Card Draw

*For any* completed round, each player should draw 3 new cards from the draw pile (if available).

**Validates: Requirements 4.7**

### Property 15: Suit Abilities Only on Numbered Cards

*For any* face card (Ace, Jack, Queen, King), suit abilities (Club, Spade, Heart, Diamond) should not activate regardless of the card's suit.

**Validates: Requirements 6.2, 7.2, 8.2, 9.3**

### Property 16: Club Ability Damage Bonus

*For any* numbered Club card and any vault size, the damage bonus should equal floor(vault_size / 2).

**Validates: Requirements 6.1**

### Property 17: Spade Ability Defense Bonus

*For any* numbered Spade card and any vault size, the defense bonus should equal floor(vault_size / 2) and be added to current defense.

**Validates: Requirements 7.1, 7.3**

### Property 18: Heart Ability Healing

*For any* numbered Heart card played by a round winner with any vault size, healing should equal floor(vault_size / 4), and final health should not exceed 50.

**Validates: Requirements 8.1, 8.3, 17.4**

### Property 19: Diamond Ability Vault Manipulation

*For any* numbered Diamond card, a random card should be removed from a non-empty vault and shuffled back into the draw pile.

**Validates: Requirements 9.1, 9.2**

### Property 20: Ace Disables Face Abilities

*For any* round where an Ace is played, all face card abilities (Jack, Queen, King) should be disabled, but suit abilities should still activate.

**Validates: Requirements 10.1, 10.4**

### Property 21: Jack Reverses Round Logic

*For any* round with an odd number of Jacks, the player with lower standard damage should win; with an even number (including zero), the player with higher damage should win.

**Validates: Requirements 11.1, 11.3**

### Property 22: Jack Reversed Damage Application

*For any* round with Jack reversal active, the loser should take damage equal to the difference between the two players' standard damage values.

**Validates: Requirements 11.2**

### Property 23: Jack Does Not Affect King

*For any* round with both Jack and King abilities, King's true damage should apply normally regardless of Jack's reversal effect.

**Validates: Requirements 11.4, 13.5**

### Property 24: Queen Ability Disabling

*For any* Queen played, the player should be able to disable 2 opponent abilities if their vault is smaller, or 1 opponent ability if their vault is larger or equal.

**Validates: Requirements 12.1, 12.2, 12.3**

### Property 25: King True Damage and Vault Reduction

*For any* King played against an opponent with vault size V, true damage should equal V, and the opponent's vault should be reduced by floor(V / 4) cards which are removed from the game.

**Validates: Requirements 13.1, 13.2, 13.3**

### Property 26: King Ability Non-Stacking

*For any* round where multiple Kings are played by the same player, the King ability should activate only once.

**Validates: Requirements 13.4**

### Property 27: Defense Blocks Standard Damage

*For any* player with defense D receiving standard damage S, if S ≤ D, health should not decrease and defense should become D - S; if S > D, defense should become 0 and health should decrease by S - D.

**Validates: Requirements 14.1, 14.2**

### Property 28: Defense Decay

*For any* player with defense D at the start of a round, defense should decrease by floor(D / 4) before card selection.

**Validates: Requirements 14.3, 25.3**

### Property 29: Defense Persistence

*For any* defense value after decay and ability bonuses, it should persist to the next round (subject to further decay).

**Validates: Requirements 14.4**

### Property 30: True Damage Bypasses Defense

*For any* player receiving true damage T, health should decrease by T regardless of defense value, and defense should remain unchanged.

**Validates: Requirements 14.5, 15.1, 15.4**

### Property 31: True Damage Cancellation

*For any* two players dealing true damage T1 and T2 to each other, the net true damage should be |T1 - T2| applied to the player who dealt less.

**Validates: Requirements 15.2**

### Property 32: True Damage Excluded from Winner Calculation

*For any* round, the winner should be determined solely by net standard damage, with true damage not contributing to the winner determination.

**Validates: Requirements 15.3**

### Property 33: Card Shedding Mechanics

*For any* player shedding N cards from their vault, N random cards should be removed from the vault and from the game, and the player should receive N benefits (each being +1 damage, +1 defense, or +1 health).

**Validates: Requirements 16.1, 16.2, 16.3, 16.4**

### Property 34: Health Reduction from Damage

*For any* player with health H and defense D receiving standard damage S where S > D, health should decrease by S - D.

**Validates: Requirements 17.2**

### Property 35: Healing Increases Health

*For any* player with health H receiving healing amount A, health should increase by A but not exceed 50.

**Validates: Requirements 17.3**

### Property 36: Health-Based Win Condition

*For any* player reaching 0 health, the game should end with the opponent declared winner, unless both reach 0 simultaneously (resulting in a tie).

**Validates: Requirements 17.5, 17.6**

### Property 37: Vault Size Tracking

*For any* vault operations (adding cards, removing cards), the vault size should accurately reflect the number of cards currently in the vault.

**Validates: Requirements 18.2**

### Property 38: Vault Cards Not Playable

*For any* card in a player's vault, it should not be selectable or playable during rounds.

**Validates: Requirements 18.3**

### Property 39: Vault-Based Win Condition

*For any* game state where the draw pile cannot provide enough cards for both players to play a full round, the game should end with the player having the larger vault declared winner, or a tie if vaults are equal.

**Validates: Requirements 18.4, 18.5, 18.6**

### Property 40: Ability Execution Order

*For any* round, abilities should execute in this exact order: (1) defense decay, (2) card shedding, (3) Ace, (4) Queen, (5) Jack & King, (6) Spade & Club, (7) score calculation, (8) Diamond, (9) Heart.

**Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.8, 19.9**

### Property 41: UI State Reflection

*For any* game state, the UI should display current values for both players' health, defense, vault size, hand cards, played cards, and round number.

**Validates: Requirements 20.1, 20.2, 20.3, 20.4, 20.5, 20.6**

### Property 42: Scene Transition Flow

*For any* game session, scenes should transition in this order: main menu → deck builder → gameplay → game over → main menu (on return).

**Validates: Requirements 21.2, 21.3, 21.4, 21.5**

### Property 43: Hand Validation

*For any* card selection attempt, only cards currently in the player's hand should be selectable.

**Validates: Requirements 22.2**

### Property 44: Turn-Based Input Blocking

*For any* game state during opponent's turn or during ability resolution animations, player input should be disabled.

**Validates: Requirements 22.4, 22.5**

### Property 45: Game Loop Structure

*For any* frame in the game loop, input events should be processed, game state should be updated, and the current scene should be rendered.

**Validates: Requirements 23.2, 23.3, 23.4**

### Property 46: Draw Pile Shuffling

*For any* new game, the 52-card deck should be shuffled before dealing initial hands.

**Validates: Requirements 24.1**

### Property 47: Draw Order

*For any* draw operation, cards should be drawn from the top of the draw pile in order.

**Validates: Requirements 24.2**

### Property 48: Draw Pile Tracking

*For any* draw pile operations (drawing cards, adding tied cards), the remaining card count should accurately reflect the number of cards in the pile.

**Validates: Requirements 24.3, 24.4**

### Property 49: Removed Cards Exclusion

*For any* cards removed by shedding or King ability, they should not appear in the draw pile, hands, or vaults until the game ends.

**Validates: Requirements 24.5**

### Property 50: Consistent Rounding

*For any* division operation in damage calculations, ability calculations, defense decay, or vault reduction, the result should be rounded down using the floor function.

**Validates: Requirements 25.1, 25.2, 25.3, 25.4**

## Error Handling

### Asset Loading Failures

**Strategy**: Graceful degradation with clear error messages.

- If critical assets (card images, fonts) fail to load, display error dialog with specific missing asset names
- Log error details to console for debugging
- Exit application cleanly without crashes
- Provide fallback to colored rectangles for cards if images unavailable

### Invalid Game States

**Strategy**: Defensive programming with state validation.

- Validate card counts before dealing (ensure deck has enough cards)
- Validate vault operations (prevent removing from empty vault)
- Validate health/defense values (prevent negative values)
- Log warnings for unexpected states
- Recover by resetting to last known good state if possible

### Input Validation Errors

**Strategy**: Silent rejection with visual feedback.

- Reject invalid card selections without error messages
- Provide visual feedback (red highlight) for invalid actions
- Disable UI elements that would cause invalid states
- Prevent double-clicks from causing duplicate actions

### Pygame Errors

**Strategy**: Catch and handle pygame-specific exceptions.

- Handle display initialization failures
- Handle audio system unavailability (continue without sound)
- Handle font rendering errors (use fallback fonts)
- Catch and log pygame.error exceptions

### Edge Cases

**Strategy**: Explicit handling of boundary conditions.

- Empty vaults: Skip vault-dependent abilities (Diamond, Club, Spade, Heart)
- Insufficient cards: End game with vault-based winner
- Zero defense: Apply full damage to health
- Maximum health: Cap healing at 50
- Division by zero: Never occurs due to floor(x/n) where n > 1

## Testing Strategy

### Unit Testing Approach

Unit tests will focus on specific examples, edge cases, and integration points between components. We'll use pytest as the testing framework.

**Key Areas for Unit Tests**:
- Card creation and attribute access (specific examples of each rank/suit)
- Player initialization with starting values (health=50, defense=0)
- Vault operations with empty vaults (edge case)
- Deck operations with insufficient cards (edge case)
- Scene transitions between specific states
- UI rendering with specific game states
- Error handling for asset loading failures

**Example Unit Tests**:
```python
def test_ace_has_base_damage_1():
    card = Card(rank='A', suit='Club')
    assert card.get_base_damage() == 1

def test_empty_vault_diamond_ability():
    # Edge case: Diamond with empty vaults should skip
    player1 = Player(player_id=1, vault=Vault())
    player2 = Player(player_id=2, vault=Vault())
    # Verify Diamond ability doesn't crash
```

### Property-Based Testing Approach

Property tests will verify universal properties across all inputs using Hypothesis (Python's property-based testing library). Each test will run a minimum of 100 iterations with randomized inputs.

**Configuration**:
```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
```

**Test Tagging Format**:
Each property test must include a comment referencing the design document property:
```python
# Feature: card-game-core, Property 1: Base Damage Calculation
@given(card=st.sampled_from(all_cards))
def test_base_damage_calculation(card):
    # Test implementation
```

**Property Test Coverage**:
- All 50 correctness properties will have corresponding property-based tests
- Generators will create random cards, players, game states, and action sequences
- Tests will verify invariants hold across all generated inputs
- Edge cases (empty vaults, zero health, etc.) will be included in generators

**Example Property Tests**:
```python
# Feature: card-game-core, Property 1: Base Damage Calculation
@given(rank=st.sampled_from(['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']),
       suit=st.sampled_from(['Club', 'Spade', 'Heart', 'Diamond']))
@settings(max_examples=100)
def test_base_damage_for_all_cards(rank, suit):
    card = Card(rank=rank, suit=suit)
    damage = card.get_base_damage()
    
    if rank == 'A':
        assert damage == 1
    elif rank in ['J', 'Q', 'K']:
        assert damage == 10
    else:
        assert damage == int(rank)

# Feature: card-game-core, Property 27: Defense Blocks Standard Damage
@given(defense=st.integers(min_value=0, max_value=100),
       damage=st.integers(min_value=0, max_value=100),
       initial_health=st.integers(min_value=1, max_value=50))
@settings(max_examples=100)
def test_defense_blocks_standard_damage(defense, damage, initial_health):
    player = Player(player_id=1, health=initial_health, defense=defense)
    player.take_damage(standard_dmg=damage, true_dmg=0)
    
    if damage <= defense:
        assert player.health == initial_health
        assert player.defense == defense - damage
    else:
        assert player.health == initial_health - (damage - defense)
        assert player.defense == 0
```

**Generators for Complex Types**:
```python
@st.composite
def card_strategy(draw):
    rank = draw(st.sampled_from(['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']))
    suit = draw(st.sampled_from(['Club', 'Spade', 'Heart', 'Diamond']))
    return Card(rank=rank, suit=suit)

@st.composite
def player_strategy(draw):
    health = draw(st.integers(min_value=0, max_value=50))
    defense = draw(st.integers(min_value=0, max_value=50))
    vault_size = draw(st.integers(min_value=0, max_value=26))
    return Player(player_id=1, health=health, defense=defense, 
                  vault=create_vault_with_size(vault_size))
```

### Integration Testing

Integration tests will verify interactions between systems:
- Combat_System + Ability_Resolver: Full round resolution
- Scene_Manager + Input_Handler: Scene transitions with user input
- UI_Manager + Game state: Display updates reflecting state changes
- Deck_Builder + Combat_System: Deck creation through first round

### Testing Balance

- Unit tests: ~30 tests for specific examples and edge cases
- Property tests: 50 tests (one per correctness property)
- Integration tests: ~10 tests for system interactions
- Total: ~90 automated tests

This dual approach ensures both concrete correctness (unit tests) and comprehensive coverage (property tests), with property tests handling the bulk of input variation testing.

