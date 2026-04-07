# Requirements Document

## Introduction

This document specifies the requirements for a strategic two-player card game built with Python and pygame. The game features simultaneous card play, resource management through a vault system, and complex card interactions with health, defense, and damage mechanics. Players compete through rounds of tactical card selection, managing their resources to reduce their opponent's health to zero or accumulate the largest vault.

## Glossary

- **Game_Engine**: The core pygame-based system managing the game loop, rendering, and state
- **Deck_Builder**: The system allowing players to construct their 26-card decks
- **Combat_System**: The system that resolves card interactions, calculates damage, and determines round winners
- **Vault**: A player's collection of won cards that powers various abilities
- **Card**: A game object with rank, suit, and associated abilities
- **Player**: A participant in the game with health, defense, vault, hand, and deck
- **Round**: A single cycle of card play where both players select 3 cards, reveal simultaneously, and resolve combat
- **Ability_Resolver**: The system that executes card abilities in the correct order
- **UI_Manager**: The system that displays game state, cards, and player statistics
- **Input_Handler**: The system that processes mouse input for card selection and placement
- **Scene_Manager**: The system that manages transitions between game states (menu, deck building, gameplay, game over)
- **Standard_Damage**: Damage that cancels opposing damage point-for-point and is blocked by defense
- **True_Damage**: Damage that bypasses defense and only cancels opposing true damage
- **Defense**: A persistent stat that blocks standard damage and decays each round
- **Card_Shedding**: The mechanic allowing players to remove vault cards for stat boosts

## Requirements

### Requirement 1: Game Initialization

**User Story:** As a player, I want the game to initialize properly, so that I can start playing without errors.

#### Acceptance Criteria

1. THE Game_Engine SHALL initialize pygame with a window resolution of 1280x720 pixels
2. THE Game_Engine SHALL set the target frame rate to 60 frames per second
3. THE Game_Engine SHALL load all required assets before gameplay begins
4. THE Scene_Manager SHALL display the main menu scene upon successful initialization
5. IF asset loading fails, THEN THE Game_Engine SHALL display an error message and exit gracefully

### Requirement 2: Deck Construction

**User Story:** As a player, I want to build a custom deck, so that I can use my preferred strategy.

#### Acceptance Criteria

1. THE Deck_Builder SHALL allow each player to select exactly 26 cards from a standard 52-card deck
2. THE Deck_Builder SHALL prevent players from selecting the same card
3. WHEN both players have selected 26 cards, THE Deck_Builder SHALL combine the selections into a single 52-card game deck
4. THE Deck_Builder SHALL shuffle the combined deck before gameplay begins
5. THE Deck_Builder SHALL deal 6 cards to each player as their starting hand

### Requirement 3: Card Selection and Placement

**User Story:** As a player, I want to select and place cards during my turn, so that I can participate in rounds.

#### Acceptance Criteria

1. THE Input_Handler SHALL allow players to select up to 3 cards from their hand using mouse clicks
2. THE Input_Handler SHALL provide visual feedback when a card is selected
3. THE Input_Handler SHALL allow players to deselect cards before confirming their selection
4. WHEN a player has selected 3 cards, THE Input_Handler SHALL allow the player to confirm their selection
5. THE Game_Engine SHALL display selected cards face down until both players have confirmed
6. THE Input_Handler SHALL prevent players from modifying their selection after confirmation

### Requirement 4: Card Reveal and Combat Resolution

**User Story:** As a player, I want cards to be revealed and resolved correctly, so that the game follows the rules.

#### Acceptance Criteria

1. WHEN both players have confirmed their card selections, THE Game_Engine SHALL reveal all 6 cards simultaneously
2. THE Combat_System SHALL calculate damage for each card based on its rank
3. THE Ability_Resolver SHALL execute card abilities in the specified order of operations
4. THE Combat_System SHALL determine the round winner based on net standard damage dealt
5. WHEN a player wins a round, THE Combat_System SHALL add all 6 played cards to the winner's vault
6. IF both players deal equal net damage, THEN THE Combat_System SHALL shuffle all 6 cards back into the draw pile
7. THE Combat_System SHALL draw 3 new cards for each player after round resolution

### Requirement 5: Base Damage Calculation

**User Story:** As a player, I want cards to deal damage based on their rank, so that card values matter.

#### Acceptance Criteria

1. WHEN an Ace is played, THE Combat_System SHALL calculate 1 base damage
2. WHEN a numbered card (2-10) is played, THE Combat_System SHALL calculate base damage equal to the card number
3. WHEN a face card (Jack, Queen, King) is played, THE Combat_System SHALL calculate 10 base damage
4. THE Combat_System SHALL sum all base damage from a player's 3 cards before applying abilities

### Requirement 6: Club Suit Ability

**User Story:** As a player, I want Club cards to boost my damage, so that I can leverage my vault size.

#### Acceptance Criteria

1. WHEN a numbered Club card is played, THE Ability_Resolver SHALL add damage equal to half the player's vault size rounded down
2. THE Ability_Resolver SHALL NOT apply Club ability to face cards with Club suit
3. THE Ability_Resolver SHALL calculate vault size before applying the Club ability

### Requirement 7: Spade Suit Ability

**User Story:** As a player, I want Spade cards to grant defense, so that I can protect my health.

#### Acceptance Criteria

1. WHEN a numbered Spade card is played, THE Ability_Resolver SHALL add defense equal to half the player's vault size rounded down
2. THE Ability_Resolver SHALL NOT apply Spade ability to face cards with Spade suit
3. THE Combat_System SHALL add the defense bonus to the player's current defense value

### Requirement 8: Heart Suit Ability

**User Story:** As a player, I want Heart cards to heal me when I win, so that I can recover health.

#### Acceptance Criteria

1. WHEN a player wins a round with a numbered Heart card, THE Ability_Resolver SHALL heal the player by one-fourth of their vault size rounded down
2. THE Ability_Resolver SHALL NOT apply Heart ability to face cards with Heart suit
3. THE Combat_System SHALL NOT allow healing to exceed the starting health of 50
4. THE Ability_Resolver SHALL apply Heart ability after the round winner is determined

### Requirement 9: Diamond Suit Ability

**User Story:** As a player, I want Diamond cards to manipulate vaults, so that I can disrupt my opponent's strategy.

#### Acceptance Criteria

1. WHEN a numbered Diamond card is played, THE Ability_Resolver SHALL force the player to choose a random card from either player's vault
2. THE Ability_Resolver SHALL shuffle the chosen card back into the draw pile
3. THE Ability_Resolver SHALL NOT apply Diamond ability to face cards with Diamond suit
4. IF a vault is empty, THEN THE Ability_Resolver SHALL only allow selection from the non-empty vault
5. IF both vaults are empty, THEN THE Ability_Resolver SHALL skip the Diamond ability

### Requirement 10: Ace Face Card Ability

**User Story:** As a player, I want Aces to disable face card abilities, so that I can counter powerful plays.

#### Acceptance Criteria

1. WHEN an Ace is played, THE Ability_Resolver SHALL disable all face card abilities for the current round
2. THE Ability_Resolver SHALL execute Ace ability before cards are revealed
3. WHEN a player announces an Ace and the opponent plays a Queen, THE Ability_Resolver SHALL allow the opponent to choose which abilities to disable if the player does not have an Ace
4. THE Ability_Resolver SHALL NOT disable suit abilities when Ace is played

### Requirement 11: Jack Face Card Ability

**User Story:** As a player, I want Jacks to reverse round logic, so that I can win with lower damage.

#### Acceptance Criteria

1. WHEN a Jack is played, THE Combat_System SHALL reverse the round logic so that lower damage wins
2. WHEN the round logic is reversed, THE Combat_System SHALL apply damage equal to the difference to the loser
3. WHEN multiple Jacks are played, THE Combat_System SHALL flip the logic for each Jack
4. THE Combat_System SHALL NOT reverse King true damage with Jack ability

### Requirement 12: Queen Face Card Ability

**User Story:** As a player, I want Queens to disable opponent abilities, so that I can neutralize threats.

#### Acceptance Criteria

1. WHEN a Queen is played, THE Ability_Resolver SHALL allow the player to disable opponent card abilities before reveal
2. WHEN the player has a smaller vault, THE Ability_Resolver SHALL allow disabling 2 opponent abilities
3. WHEN the player has a larger or equal vault, THE Ability_Resolver SHALL allow disabling 1 opponent ability
4. THE Ability_Resolver SHALL execute Queen ability before cards are revealed

### Requirement 13: King Face Card Ability

**User Story:** As a player, I want Kings to deal true damage, so that I can bypass defense.

#### Acceptance Criteria

1. WHEN a King is played, THE Combat_System SHALL deal true damage equal to the opponent's vault size
2. THE Combat_System SHALL reduce the affected player's vault by one-fourth rounded down
3. THE Combat_System SHALL remove lost vault cards from the game until it ends
4. WHEN multiple Kings are played, THE Combat_System SHALL activate the ability only once
5. THE Combat_System SHALL NOT reverse King ability with Jack

### Requirement 14: Defense Mechanics

**User Story:** As a player, I want defense to protect my health, so that I can survive longer.

#### Acceptance Criteria

1. THE Combat_System SHALL block standard damage with defense on a point-for-point basis
2. WHEN standard damage exceeds defense, THE Combat_System SHALL reduce health by the remaining damage
3. THE Combat_System SHALL reduce each player's defense by one-fourth rounded down at the start of each round
4. THE Combat_System SHALL maintain defense values between rounds
5. THE Combat_System SHALL NOT block true damage with defense

### Requirement 15: True Damage Mechanics

**User Story:** As a player, I want true damage to bypass defense, so that King abilities are powerful.

#### Acceptance Criteria

1. THE Combat_System SHALL apply true damage directly to health
2. THE Combat_System SHALL cancel opposing true damage point-for-point
3. THE Combat_System SHALL NOT include true damage in round winner calculation
4. THE Combat_System SHALL NOT block true damage with defense

### Requirement 16: Card Shedding

**User Story:** As a player, I want to shed vault cards for bonuses, so that I can make tactical trades.

#### Acceptance Criteria

1. THE Input_Handler SHALL allow players to shed any number of vault cards at the beginning of each round
2. WHEN a player sheds a card, THE Combat_System SHALL remove a random card from the player's vault
3. THE Combat_System SHALL remove shed cards from the game until it ends
4. WHEN a player sheds a card, THE Input_Handler SHALL allow the player to choose one benefit: +1 damage, +1 defense, or +1 health
5. THE Combat_System SHALL apply shedding bonuses before card reveal

### Requirement 17: Health Management

**User Story:** As a player, I want health to be tracked accurately, so that win conditions work correctly.

#### Acceptance Criteria

1. THE Combat_System SHALL initialize each player with 50 health at game start
2. THE Combat_System SHALL reduce health when damage exceeds defense
3. THE Combat_System SHALL increase health when healing is applied
4. THE Combat_System SHALL NOT allow health to exceed 50
5. WHEN a player's health reaches 0, THE Combat_System SHALL end the game and declare the opponent the winner
6. IF both players reach 0 health in the same round, THEN THE Combat_System SHALL declare a tie

### Requirement 18: Vault Management

**User Story:** As a player, I want my vault to be managed correctly, so that abilities work as intended.

#### Acceptance Criteria

1. THE Combat_System SHALL add all 6 played cards to the winner's vault after each round
2. THE Combat_System SHALL track vault size for each player
3. THE Combat_System SHALL prevent players from using vault cards during rounds
4. WHEN the draw pile is empty and players cannot play a full round, THE Combat_System SHALL end the game
5. WHEN the game ends due to insufficient cards, THE Combat_System SHALL declare the player with the larger vault the winner
6. IF both players have equal vault sizes when the game ends, THEN THE Combat_System SHALL declare a tie

### Requirement 19: Order of Operations

**User Story:** As a player, I want abilities to resolve in the correct order, so that the game is fair and predictable.

#### Acceptance Criteria

1. THE Ability_Resolver SHALL decrease each player's defense by one-fourth rounded down before card selection
2. THE Ability_Resolver SHALL process card shedding after defense decay
3. THE Ability_Resolver SHALL execute Ace ability after shedding
4. THE Ability_Resolver SHALL execute Queen ability after Ace
5. THE Ability_Resolver SHALL execute Jack and King abilities after card reveal
6. THE Ability_Resolver SHALL execute Spade and Club abilities after Jack and King
7. THE Ability_Resolver SHALL calculate scores after Spade and Club
8. THE Ability_Resolver SHALL execute Diamond ability after score calculation
9. THE Ability_Resolver SHALL execute Heart ability after the winner is decided

### Requirement 20: User Interface Display

**User Story:** As a player, I want to see game state clearly, so that I can make informed decisions.

#### Acceptance Criteria

1. THE UI_Manager SHALL display each player's current health
2. THE UI_Manager SHALL display each player's current defense
3. THE UI_Manager SHALL display each player's vault size
4. THE UI_Manager SHALL display each player's hand with selectable cards
5. THE UI_Manager SHALL display played cards during reveal and resolution
6. THE UI_Manager SHALL display the current round number
7. THE UI_Manager SHALL provide visual feedback for card selection and ability activation

### Requirement 21: Scene Management

**User Story:** As a player, I want to navigate between game screens, so that I can access all game features.

#### Acceptance Criteria

1. THE Scene_Manager SHALL display a main menu scene with options to start a game or exit
2. THE Scene_Manager SHALL transition to the deck builder scene when starting a new game
3. THE Scene_Manager SHALL transition to the gameplay scene after deck construction
4. THE Scene_Manager SHALL transition to the game over scene when a win condition is met
5. THE Scene_Manager SHALL allow returning to the main menu from the game over scene

### Requirement 22: Input Validation

**User Story:** As a player, I want invalid inputs to be rejected, so that the game doesn't break.

#### Acceptance Criteria

1. THE Input_Handler SHALL prevent selecting more than 3 cards per round
2. THE Input_Handler SHALL prevent selecting cards not in the player's hand
3. THE Input_Handler SHALL prevent confirming selection with fewer than 3 cards
4. THE Input_Handler SHALL prevent interaction during opponent's turn
5. THE Input_Handler SHALL prevent interaction during ability resolution animations

### Requirement 23: Game Loop

**User Story:** As a player, I want the game to run smoothly, so that gameplay is enjoyable.

#### Acceptance Criteria

1. THE Game_Engine SHALL maintain a consistent frame rate of 60 frames per second
2. THE Game_Engine SHALL process input events each frame
3. THE Game_Engine SHALL update game state each frame
4. THE Game_Engine SHALL render the current scene each frame
5. THE Game_Engine SHALL handle window close events gracefully

### Requirement 24: Draw Pile Management

**User Story:** As a player, I want the draw pile to be managed correctly, so that card distribution is fair.

#### Acceptance Criteria

1. THE Combat_System SHALL shuffle the 52-card deck before dealing initial hands
2. THE Combat_System SHALL draw cards from the top of the draw pile
3. THE Combat_System SHALL track the number of cards remaining in the draw pile
4. WHEN tied rounds occur, THE Combat_System SHALL shuffle the 6 played cards back into the draw pile
5. THE Combat_System SHALL NOT include shed cards or King-removed cards in the draw pile

### Requirement 25: Rounding Rules

**User Story:** As a player, I want calculations to be consistent, so that the game is predictable.

#### Acceptance Criteria

1. THE Combat_System SHALL round down all division results using the floor function
2. THE Ability_Resolver SHALL round down vault-based calculations for Club, Spade, Heart, and King abilities
3. THE Combat_System SHALL round down defense decay calculations
4. THE Combat_System SHALL round down vault reduction from King ability

