# Game Rules

## Overview

A strategic two-player card game using a custom 52-card deck where players compete through rounds of simultaneous card play, managing health, defense, and vault resources.

## Setup

### Deck Construction
- Each player picks 26 cards from different decks
- Both sets combine into a single 52-card deck for gameplay
- Each player is dealt 6 cards to start

## Core Mechanics

### Round Structure
1. Each player selects 3 cards from their hand and places them face down
2. All 6 cards are revealed simultaneously
3. Cards deal damage according to their abilities
4. Winner takes all 6 cards to their vault
5. If damage is equal, all 6 cards shuffle back into draw pile
6. Each player draws 3 new cards before the next round

### The Vault
- Storage for won cards
- Cards in vault cannot be used during rounds
- Vault size affects various card abilities
- Vault size determines winner if game ends without health reaching 0

## Card Values and Abilities

### Base Damage
- Ace: 1 damage
- Numbered cards (2-10): Damage equal to card number
- Face cards (Jack, Queen, King): 10 damage

### Suit Abilities (Numbered Cards Only)
- **Club**: Add damage equal to half of player's vault size (rounded down)
- **Spade**: Add defense equal to half of player's vault size (rounded down)
- **Heart**: Upon winning round, heal by one-fourth of vault size (rounded down)
- **Diamond**: Force player to choose random card from either vault to shuffle back into draw pile

### Face Card Abilities (Override Suit Abilities)

**Ace**
- Disables all face card abilities for the round
- Announced before cards are revealed
- If player lies about ace and opponent plays Queen, opponent chooses which abilities to disable

**Jack**
- Reverses round logic: lower damage wins
- Loser takes damage equal to difference
- Multiple Jacks flip logic repeatedly (2 Jacks = normal logic)

**Queen**
- Allows disabling opponent's card abilities before reveal
- Smaller vault: disable 2 opponent abilities
- Larger vault: disable 1 opponent ability
- Equal vault: disable 1 opponent ability

**King**
- Deals true damage equal to opponent's vault size
- Ability does not stack (multiple Kings = single activation)
- Affected player loses one-fourth of vault (rounded down)
- Lost cards removed from game until it ends
- Not affected by Jack reversal

## Combat Mechanics

### Damage Types

**Standard Damage**
- Cancels opposing damage point-for-point
- Remaining damage reduces defense first
- After defense reaches 0, reduces health

**Defense**
- Blocks standard damage point-for-point
- Persists between rounds
- Loses one-fourth (rounded down) at start of each round

**Healing**
- Increases health by points healed
- Cannot exceed starting health (50)

**True Damage**
- Only from King ability
- Bypasses defense entirely
- Only canceled by opposing true damage
- Directly reduces health

### Card Shedding

At the beginning of each round, players may shed cards:
- Removes random card from player's vault
- Removed card is lost from game until it ends
- Grants one benefit per shed:
  - +1 damage to current round, OR
  - +1 defense to current amount, OR
  - +1 health to current amount

## Winning Conditions

### Win by Health
- Opponent's health reaches 0
- Each player starts with 50 health
- Both reaching 0 in same round = tie

### Win by Vault
- Players cannot play a full round (insufficient cards)
- Player with larger vault wins
- Equal vaults = tie

### Winning a Round
- Deal more net damage after opposing damages cancel
- Defense and true damage don't count toward round victory
- Winner takes all 6 played cards to vault

## Order of Operations

### Before Revealing Cards
1. Each player's defense decreases by one-fourth (rounded down)
2. Each player chooses to shed any number of cards
3. Ace ability activates
4. Queen ability activates

### After Revealing Cards
1. Jack and King abilities activate
2. Spade and Club abilities activate
3. Scores are calculated
4. Diamond ability activates

### After Winner is Decided
1. Heart ability activates

## Implementation Notes

- All rounding is done downward (floor function)
- Cards removed by King or shedding are tracked separately from draw pile
- Defense persists between rounds but decays
- Vault size is critical for many abilities
- Face cards do NOT trigger their suit abilities
