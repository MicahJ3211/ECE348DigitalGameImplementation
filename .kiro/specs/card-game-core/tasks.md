# Implementation Plan: Card Game Core

## Overview

This implementation plan breaks down the card game core feature into discrete coding tasks. The approach follows a bottom-up strategy: building foundational entities and data models first, then systems that operate on them, and finally the game engine and UI layer. Each task builds incrementally, with checkpoints to validate functionality.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure following structure.md conventions (src/, assets/, tests/)
  - Create requirements.txt with pygame, pytest, hypothesis dependencies
  - Create src/config.py with game constants (SCREEN_WIDTH=1280, SCREEN_HEIGHT=720, FPS=60, STARTING_HEALTH=50)
  - Set up pytest configuration for test discovery
  - _Requirements: 1.1, 1.2_

- [x] 2. Implement core entity classes
  - [x] 2.1 Create Card entity with data model and methods
    - Implement Card dataclass with rank and suit attributes
    - Implement get_base_damage() method (Ace=1, 2-10=rank, Face=10)
    - Implement is_face_card() and is_numbered_card() helper methods
    - Implement get_suit_ability() and get_face_ability() methods
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 2.2 Write property test for Card base damage calculation
    - **Property 1: Base Damage Calculation**
    - **Validates: Requirements 5.1, 5.2, 5.3**
  
  - [x] 2.3 Create Vault entity with card storage operations
    - Implement Vault class with internal card list
    - Implement add_cards(), remove_random_card(), remove_cards_from_game() methods
    - Implement size(), is_empty() query methods
    - _Requirements: 18.1, 18.2_
  
  - [x] 2.4 Write property test for Vault size tracking
    - **Property 37: Vault Size Tracking**
    - **Validates: Requirements 18.2**
  
  - [x] 2.5 Create Deck entity with shuffling and drawing
    - Implement Deck class with card list initialization
    - Implement shuffle() using random.shuffle
    - Implement draw(), add_cards(), remaining(), can_draw() methods
    - _Requirements: 2.4, 24.1, 24.2, 24.3_
  
  - [x] 2.6 Write property tests for Deck operations
    - **Property 5: Deck Shuffling**
    - **Property 47: Draw Order**
    - **Property 48: Draw Pile Tracking**
    - **Validates: Requirements 2.4, 24.1, 24.2, 24.3**

- [x] 3. Implement Player entity with health and defense mechanics
  - [x] 3.1 Create Player dataclass with core attributes
    - Implement Player dataclass with player_id, health, defense, vault, hand, deck
    - Initialize with health=50, defense=0
    - _Requirements: 17.1_
  
  - [x] 3.2 Implement damage application methods
    - Implement take_damage(standard_dmg, true_dmg) with defense blocking logic
    - Implement heal(amount) with 50 health cap
    - Implement add_defense(amount) method
    - _Requirements: 14.1, 14.2, 14.5, 17.2, 17.3, 17.4_
  
  - [x] 3.3 Write property tests for damage and defense mechanics
    - **Property 27: Defense Blocks Standard Damage**
    - **Property 30: True Damage Bypasses Defense**
    - **Property 35: Healing Increases Health**
    - **Validates: Requirements 14.1, 14.2, 14.5, 17.2, 17.3, 17.4**
  
  - [x] 3.4 Implement defense decay and card management
    - Implement decay_defense() method (reduce by floor(defense / 4))
    - Implement draw_cards(count) method
    - Implement shed_card(bonus_type) method
    - _Requirements: 14.3, 16.1, 16.2, 25.3_
  
  - [x] 3.5 Write property tests for defense decay and shedding
    - **Property 28: Defense Decay**
    - **Property 33: Card Shedding Mechanics**
    - **Validates: Requirements 14.3, 16.1, 16.2, 16.3, 16.4, 25.3**

- [x] 4. Checkpoint - Ensure entity tests pass
  - Run pytest on entity tests
  - Verify all property tests pass with 100+ iterations
  - Ask the user if questions arise

- [x] 5. Implement result data models
  - [x] 5.1 Create RoundResult dataclass
    - Define RoundResult with winner_id, damage values, played_cards, abilities_activated
    - _Requirements: 4.4, 4.5_
  
  - [x] 5.2 Create AbilityResult dataclass
    - Define AbilityResult with damage_modifiers, defense_modifiers, disabled_abilities, jack_count, king_activated
    - _Requirements: 19.1_
  
  - [x] 5.3 Create WinCondition dataclass
    - Define WinCondition with game_over, winner_id, reason
    - _Requirements: 17.5, 18.4_

- [x] 6. Implement Combat_System for round resolution
  - [x] 6.1 Create Combat_System class with base damage calculation
    - Implement calculate_base_damage(cards) method
    - Sum base damage from 3 cards
    - _Requirements: 5.4_
  
  - [x] 6.2 Write property test for damage summation
    - **Property 2: Damage Summation**
    - **Validates: Requirements 5.4**
  
  - [x] 6.3 Implement damage application logic
    - Implement apply_damage(player, standard_dmg, true_dmg) method
    - Handle defense blocking for standard damage
    - Apply true damage directly to health
    - _Requirements: 14.1, 14.2, 15.1_
  
  - [x] 6.4 Implement round winner determination
    - Implement determine_winner(p1_damage, p2_damage, jack_count) method
    - Handle Jack reversal logic (odd count reverses)
    - _Requirements: 4.4, 11.1, 11.3_
  
  - [x] 6.5 Write property tests for winner determination
    - **Property 11: Round Winner Determination**
    - **Property 21: Jack Reverses Round Logic**
    - **Validates: Requirements 4.4, 11.1, 11.3**
  
  - [x] 6.6 Implement vault and win condition management
    - Implement add_to_vault(player, cards) method
    - Implement check_win_condition(player1, player2) method
    - Handle health-based and vault-based win conditions
    - _Requirements: 4.5, 17.5, 17.6, 18.4, 18.5, 18.6_
  
  - [x] 6.7 Write property tests for vault and win conditions
    - **Property 12: Vault Addition on Win**
    - **Property 36: Health-Based Win Condition**
    - **Property 39: Vault-Based Win Condition**
    - **Validates: Requirements 4.5, 17.5, 17.6, 18.4, 18.5, 18.6**
  
  - [x] 6.8 Implement main resolve_round method
    - Wire together all combat resolution steps
    - Return RoundResult with complete round data
    - Handle tied rounds (shuffle cards back)
    - _Requirements: 4.1, 4.6, 4.7_
  
  - [x] 6.9 Write property test for tied round handling
    - **Property 13: Tied Round Handling**
    - **Validates: Requirements 4.6**

- [x] 7. Implement Ability_Resolver for card abilities
  - [x] 7.1 Create Ability_Resolver class structure
    - Initialize with reference to Combat_System
    - Create placeholder methods for ability execution phases
    - _Requirements: 19.1_
  
  - [x] 7.2 Implement pre-reveal abilities (Ace and Queen)
    - Implement execute_pre_reveal_abilities() method
    - Handle Ace ability (disable all face abilities)
    - Handle Queen ability (disable opponent abilities based on vault size)
    - _Requirements: 10.1, 10.4, 12.1, 12.2, 12.3, 19.3, 19.4_
  
  - [x] 7.3 Write property tests for Ace and Queen abilities
    - **Property 20: Ace Disables Face Abilities**
    - **Property 24: Queen Ability Disabling**
    - **Validates: Requirements 10.1, 10.4, 12.1, 12.2, 12.3**
  
  - [x] 7.4 Implement post-reveal abilities (Jack, King, Spade, Club)
    - Implement execute_post_reveal_abilities() method
    - Handle Jack ability (reverse logic, track count)
    - Handle King ability (true damage, vault reduction, non-stacking)
    - Handle Spade ability (defense bonus = floor(vault_size / 2))
    - Handle Club ability (damage bonus = floor(vault_size / 2))
    - _Requirements: 6.1, 7.1, 11.1, 11.2, 11.3, 11.4, 13.1, 13.2, 13.3, 13.4, 13.5, 19.5, 19.6_
  
  - [x] 7.5 Write property tests for Jack and King abilities
    - **Property 22: Jack Reversed Damage Application**
    - **Property 23: Jack Does Not Affect King**
    - **Property 25: King True Damage and Vault Reduction**
    - **Property 26: King Ability Non-Stacking**
    - **Validates: Requirements 11.2, 11.4, 13.1, 13.2, 13.3, 13.4, 13.5**
  
  - [x] 7.6 Write property tests for Spade and Club abilities
    - **Property 16: Club Ability Damage Bonus**
    - **Property 17: Spade Ability Defense Bonus**
    - **Validates: Requirements 6.1, 7.1, 7.3**
  
  - [x] 7.7 Implement Diamond ability (post-score calculation)
    - Handle Diamond ability in separate method
    - Remove random card from any vault to draw pile
    - _Requirements: 9.1, 9.2, 19.7_
  
  - [x] 7.8 Write property test for Diamond ability
    - **Property 19: Diamond Ability Vault Manipulation**
    - **Validates: Requirements 9.1, 9.2**
  
  - [x] 7.9 Implement Heart ability (post-winner)
    - Implement execute_post_winner_abilities() method
    - Handle Heart ability (heal = floor(vault_size / 4), cap at 50)
    - Only activate for round winner
    - _Requirements: 8.1, 8.3, 19.9_
  
  - [x] 7.10 Write property test for Heart ability
    - **Property 18: Heart Ability Healing**
    - **Validates: Requirements 8.1, 8.3, 17.4**
  
  - [x] 7.11 Implement main resolve_abilities method
    - Wire together all ability execution phases in correct order
    - Return AbilityResult with all modifiers and flags
    - Ensure suit abilities don't activate on face cards
    - _Requirements: 6.2, 7.2, 8.2, 9.3, 19.1, 19.2, 19.8_
  
  - [x] 7.12 Write property tests for ability execution order and restrictions
    - **Property 15: Suit Abilities Only on Numbered Cards**
    - **Property 40: Ability Execution Order**
    - **Validates: Requirements 6.2, 7.2, 8.2, 9.3, 19.1-19.9**

- [x] 8. Checkpoint - Ensure combat and ability tests pass
  - Run pytest on Combat_System and Ability_Resolver tests
  - Verify property tests pass with 100+ iterations
  - Test integration between Combat_System and Ability_Resolver
  - Ask the user if questions arise

- [x] 9. Implement Deck_Builder for deck construction
  - [x] 9.1 Create Deck_Builder class with card selection tracking
    - Track each player's selected cards (max 26 per player)
    - Implement select_card(player_id, card) method
    - Prevent duplicate selections
    - _Requirements: 2.1, 2.2_
  
  - [x] 9.2 Write property tests for deck construction
    - **Property 3: Duplicate Card Prevention**
    - **Property 4: Deck Combination**
    - **Validates: Requirements 2.2, 2.3**
  
  - [x] 9.3 Implement deck creation and initial dealing
    - Implement is_selection_complete() method
    - Implement create_game_deck() method (combine + shuffle)
    - Implement deal_initial_hands(deck, players) method (6 cards each)
    - _Requirements: 2.3, 2.4, 2.5_
  
  - [x] 9.4 Write property test for initial hand dealing
    - **Property 6: Initial Hand Dealing**
    - **Validates: Requirements 2.5**

- [x] 10. Implement Input_Handler for mouse input
  - [x] 10.1 Create Input_Handler class with event processing
    - Implement handle_event(event, scene) method
    - Track mouse position and clicks
    - _Requirements: 3.1, 22.1_
  
  - [x] 10.2 Implement card selection logic
    - Implement get_hovered_card(mouse_pos, cards) method
    - Implement is_valid_selection(selected_cards, hand) method
    - Validate selection count (exactly 3 cards)
    - Handle selection and deselection
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 22.2, 22.3_
  
  - [x] 10.3 Write property tests for card selection
    - **Property 7: Card Selection Limit**
    - **Property 8: Selection Reversibility**
    - **Property 43: Hand Validation**
    - **Validates: Requirements 3.1, 3.3, 22.1, 22.2, 22.3**
  
  - [x] 10.4 Implement selection locking and turn-based blocking
    - Prevent modification after confirmation
    - Block input during opponent turn and animations
    - _Requirements: 3.6, 22.4, 22.5_
  
  - [x] 10.5 Write property tests for input validation
    - **Property 9: Selection Lock After Confirmation**
    - **Property 44: Turn-Based Input Blocking**
    - **Validates: Requirements 3.6, 22.4, 22.5**

- [x] 11. Implement UI_Manager for rendering game state
  - [x] 11.1 Create UI_Manager class with pygame surface
    - Initialize with screen surface reference
    - Set up font loading with fallback
    - _Requirements: 1.3, 20.1_
  
  - [x] 11.2 Implement player stats rendering
    - Implement render_player_stats(player, position) method
    - Display health bars (top and bottom)
    - Display defense values with shield icon
    - Display vault sizes with card stack icon
    - _Requirements: 20.2, 20.3, 20.4_
  
  - [x] 11.3 Implement card rendering
    - Implement render_hand(cards, selected) method
    - Implement render_played_cards(cards, revealed) method
    - Use colored rectangles as fallback if images unavailable
    - Highlight selected cards
    - _Requirements: 3.2, 20.5_
  
  - [x] 11.4 Implement round info and ability animations
    - Implement render_round_info(round_num, phase) method
    - Implement show_ability_animation(ability, target) method (placeholder for now)
    - _Requirements: 20.6_
  
  - [x] 11.5 Write property test for UI state reflection
    - **Property 41: UI State Reflection**
    - **Validates: Requirements 20.1, 20.2, 20.3, 20.4, 20.5, 20.6**

- [x] 12. Implement Scene classes
  - [x] 12.1 Create base Scene abstract class
    - Define interface: update(delta_time), render(screen), handle_input(event)
    - _Requirements: 21.1_
  
  - [x] 12.2 Implement MenuScene
    - Display "Start Game" and "Exit" buttons
    - Handle button clicks to transition to DeckBuilderScene
    - _Requirements: 21.2_
  
  - [x] 12.3 Implement DeckBuilderScene
    - Display available cards for selection
    - Use Deck_Builder to track selections
    - Transition to GameplayScene when complete
    - _Requirements: 21.3_
  
  - [x] 12.4 Implement GameplayScene with round management
    - Initialize two Player instances
    - Manage round loop: selection → reveal → resolution → draw
    - Use Combat_System and Ability_Resolver for round resolution
    - Handle defense decay at round start
    - Handle card shedding before selection
    - Transition to GameOverScene on win condition
    - _Requirements: 4.1, 4.7, 19.2, 21.4, 25.3_
  
  - [x] 12.5 Write property tests for gameplay flow
    - **Property 10: Simultaneous Reveal**
    - **Property 14: Post-Round Card Draw**
    - **Validates: Requirements 4.1, 4.7**
  
  - [x] 12.6 Implement GameOverScene
    - Display winner and reason (health or vault)
    - Display "Return to Menu" button
    - Transition back to MenuScene
    - _Requirements: 21.5_

- [x] 13. Implement Scene_Manager for scene transitions
  - [x] 13.1 Create Scene_Manager class with scene registry
    - Initialize with GameEngine reference
    - Register all scene types
    - Track current scene
    - _Requirements: 1.4, 21.1_
  
  - [x] 13.2 Implement scene transition logic
    - Implement change_scene(scene_name, **kwargs) method
    - Validate scene transition flow
    - Pass data between scenes (e.g., deck to gameplay)
    - _Requirements: 21.2, 21.3, 21.4, 21.5_
  
  - [x] 13.3 Write property test for scene transition flow
    - **Property 42: Scene Transition Flow**
    - **Validates: Requirements 21.2, 21.3, 21.4, 21.5**
  
  - [x] 13.4 Implement update and render delegation
    - Implement update(delta_time) method
    - Implement render(screen) method
    - Implement handle_input(event) method
    - Delegate to current scene
    - _Requirements: 23.2, 23.3, 23.4_

- [x] 14. Checkpoint - Ensure scene and UI tests pass
  - Run pytest on Scene, Scene_Manager, UI_Manager, and Input_Handler tests
  - Verify scene transitions work correctly
  - Test UI rendering with mock game states
  - Ask the user if questions arise

- [x] 15. Implement Game_Engine main loop
  - [x] 15.1 Create Game_Engine class with pygame initialization
    - Initialize pygame with 1280x720 window
    - Set up clock for 60 FPS
    - Initialize Scene_Manager
    - _Requirements: 1.1, 1.2, 23.1_
  
  - [x] 15.2 Implement asset loading with error handling
    - Implement load_assets() method
    - Load card images, fonts, sounds (with fallbacks)
    - Display error dialog on critical asset failure
    - Log errors to console
    - _Requirements: 1.3, 1.5_
  
  - [x] 15.3 Implement main game loop
    - Implement run() method with event → update → render cycle
    - Handle pygame events (quit, mouse)
    - Calculate delta_time for frame-independent updates
    - Maintain 60 FPS with clock.tick()
    - _Requirements: 23.1, 23.2, 23.3, 23.4_
  
  - [x] 15.4 Write property test for game loop structure
    - **Property 45: Game Loop Structure**
    - **Validates: Requirements 23.2, 23.3, 23.4**
  
  - [x] 15.5 Implement graceful shutdown
    - Implement quit() method
    - Handle window close events
    - Clean up pygame resources
    - _Requirements: 1.5_

- [x] 16. Create main.py entry point
  - [x] 16.1 Create main.py with game initialization
    - Import Game_Engine
    - Create Game_Engine instance with config values
    - Call load_assets() and handle failures
    - Call run() to start game loop
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 17. Implement comprehensive property-based tests
  - [x] 17.1 Write remaining damage and combat property tests
    - **Property 31: True Damage Cancellation**
    - **Property 32: True Damage Excluded from Winner Calculation**
    - **Property 34: Health Reduction from Damage**
    - **Validates: Requirements 15.2, 15.3, 17.2**
  
  - [x] 17.2 Write defense persistence property test
    - **Property 29: Defense Persistence**
    - **Validates: Requirements 14.4**
  
  - [x] 17.3 Write vault property tests
    - **Property 38: Vault Cards Not Playable**
    - **Validates: Requirements 18.3**
  
  - [x] 17.4 Write draw pile property tests
    - **Property 46: Draw Pile Shuffling**
    - **Property 49: Removed Cards Exclusion**
    - **Validates: Requirements 24.1, 24.5**
  
  - [x] 17.5 Write rounding consistency property test
    - **Property 50: Consistent Rounding**
    - **Validates: Requirements 25.1, 25.2, 25.3, 25.4**

- [x] 18. Write unit tests for edge cases and examples
  - [x] 18.1 Write unit tests for card examples
    - Test specific card instances (Ace of Clubs, 10 of Hearts, King of Spades)
    - Test face card suit ability exclusion
    - _Requirements: 5.1, 5.2, 5.3, 6.2, 7.2, 8.2, 9.3_
  
  - [x] 18.2 Write unit tests for empty vault edge cases
    - Test Diamond ability with empty vaults
    - Test Club/Spade abilities with empty vaults
    - Test Heart ability with empty vault
    - _Requirements: 6.1, 7.1, 8.1, 9.1_
  
  - [x] 18.3 Write unit tests for zero defense edge case
    - Test damage application with defense=0
    - _Requirements: 14.1, 14.2_
  
  - [x] 18.4 Write unit tests for maximum health edge case
    - Test healing when health=50
    - _Requirements: 17.4_
  
  - [x] 18.5 Write unit tests for insufficient cards edge case
    - Test game end when draw pile cannot provide 3 cards per player
    - _Requirements: 18.4, 24.4_
  
  - [x] 18.6 Write unit tests for asset loading failures
    - Test graceful degradation with missing images
    - Test fallback fonts
    - _Requirements: 1.5_

- [x] 19. Integration testing and final wiring
  - [x] 19.1 Write integration test for full round resolution
    - Test complete round: selection → abilities → combat → vault update → draw
    - Verify Combat_System and Ability_Resolver integration
    - _Requirements: 4.1, 4.4, 4.5, 4.7, 19.1-19.9_
  
  - [x] 19.2 Write integration test for deck building to first round
    - Test Deck_Builder → GameplayScene → first round completion
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 4.1_
  
  - [x] 19.3 Write integration test for scene transitions with input
    - Test MenuScene → DeckBuilderScene → GameplayScene → GameOverScene → MenuScene
    - _Requirements: 21.2, 21.3, 21.4, 21.5_
  
  - [x] 19.4 Write integration test for UI updates reflecting state changes
    - Test UI_Manager displays correct values after combat resolution
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6_

- [x] 20. Final checkpoint - Ensure all tests pass
  - Run full pytest suite (unit + property + integration tests)
  - Verify all 50 property tests pass with 100+ iterations each
  - Verify ~30 unit tests pass
  - Verify ~10 integration tests pass
  - Fix any failing tests
  - Ask the user if questions arise

- [x] 21. Manual gameplay verification
  - Run the game manually (python main.py)
  - Test deck building flow
  - Play through multiple rounds
  - Verify all abilities activate correctly
  - Verify win conditions trigger properly
  - Test edge cases (empty vaults, tied rounds, etc.)
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties (50 total)
- Unit tests validate specific examples and edge cases (~30 total)
- Integration tests validate system interactions (~10 total)
- All rounding operations use floor function (round down)
- Defense persists between rounds but decays by 1/4 each round
- Face cards do NOT trigger their suit abilities
- Order of operations is critical for ability resolution
- The implementation follows a bottom-up approach: entities → systems → scenes → engine
