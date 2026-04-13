# Change Log

## 2026-04-05

### Simulation increased to 200 games
- AI Battle simulation now runs 200 games instead of 40
- Button text and loading message updated to reflect the new count

### Average vault difference stat
- Added average absolute vault size difference to simulation results summary
- Shows how far apart P1 and P2 vault sizes typically end up across all games

## 2026-04-01

### Card drafting phase
- Clicking "Play" on the menu now starts a draft phase before gameplay
- All 52 cards displayed in a grid sorted by suit, player and AI take turns picking one card at a time
- 50% chance who picks first each game
- AI picks from its top 5 highest-value available cards with some randomness
- Picked cards shown dimmed with "YOU" (blue) or "AI" (red) labels
- Yellow hover highlight on available cards during player's turn
- Player's drafted cards shown as a mini-card bar at the bottom
- Draft count displayed (You: X/26, AI: X/26)
- Press SPACE when draft is complete to start gameplay with the drafted decks
- ESC returns to menu during draft
- GameplayScene updated to accept pre-drafted card lists

### AI Battle simulation mode
- Added "AI Battle" button to main menu
- AI selection scene lets you pick two AIs from four strategies to battle
- Simulation runs 40 headless games and displays results with win/loss bar, per-game details
- "Run Again" button re-runs the same matchup; ESC returns to menu
- Four AI strategies implemented:
  - Aggressive Snowball: Clubs & high cards, builds vault for scaling damage
  - Revolutionary Saboteur: Kings & Diamonds, depletes opponent vault/health
  - Tactical Turtle: Spades & Hearts, defense wall and healing sustainability
  - Chaos Gambler: Jacks & Aces, reverses logic and disables abilities

### Scrollable results with deck viewer
- Results scene now shows all 40 games in a scrollable list (mouse wheel to scroll)
- Each row shows: game number, winner, reason, rounds, P1/P2 health, P1/P2 vault size
- Each row has "View" buttons for P1 and P2 decks
- Clicking a deck button opens a card grid showing all 26 cards sorted by suit
- Deck view shows card rank, suit, base damage, and a suit composition summary
- Back button or ESC returns to the results list

### Effect step-through with spacebar
- Replaced auto-playing ability animations with a step-by-step effect queue
- Each ability effect now shows as a centered banner; player presses SPACE to advance to the next one
- Flow: selection → reveal (face down) → SPACE to flip → step through each effect → round summary → next round

### Queen interactive disable phase
- Added `queen_disable` phase after card confirmation when the player plays a Queen
- Opponent's 3 cards shown face-down with numbered labels; player clicks to select which to disable
- Red border and "X" overlay on selected cards; auto-advances to reveal once enough cards are chosen
- Number of disables based on vault size comparison (2 if smaller vault, 1 otherwise)

### Detailed effect messages with values
- Club, Spade, Heart effects now show computed bonus values and vault size (e.g. "CLUB: You +5 damage (vault 10)")
- King effect shows damage amount and vault reduction
- Queen and Ace effects show who triggered them ("You" vs "AI")

### King ability changed to standard damage
- King's damage now goes through defense first (standard damage), no longer bypasses defense as true damage
- Vault reduction (floor(V/4) cards removed from game) unchanged
- `take_damage` still supports true_dmg parameter for future use, King just no longer uses it

### Winner ID bug fix
- Fixed mismatch between `determine_winner()` return values (1/2) and gameplay scene checks (0/1)
- Player 1 (you) winning now correctly applies damage to AI and adds cards to your vault
- Updated UI combat summary and game over scene to use correct IDs

### Card hover tooltips
- Hovering over a card in your hand during selection shows a tooltip popup above the card
- Tooltip includes card name, base damage, and ability description with current vault-based numbers
- Tooltip clamped to screen bounds, only visible during selection phase

### Ability execution order rewrite
- New order: Queen → Ace → Jack → King → Club → Spade → Diamond → Heart
- Queen resolves first so it always gets to disable opponent cards
- Ace resolves second: undoes Queen's disables (re-enables those cards), then disables all Jacks and Kings
- Effect display in gameplay follows the same order
- Refactored AbilityResolver into individual `_execute_*` methods for each ability step

### Ace undoes Queen
- When Ace is played, it clears all disables that Queen set, re-enabling those cards
- Then Ace disables J and K abilities as usual
- Queen disable phase still triggers (player still picks cards), but Ace reverses it if present
- Effect message updated: "ACE: Undoes Queen + disables Jack & King!"

### Full test suite implemented
- 237 tests: property-based (hypothesis, 100+ iterations each), unit tests, and integration tests
- Covers all 50 correctness properties from the design document
- All entities, systems, scenes, UI, and game loop tested
