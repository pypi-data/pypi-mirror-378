from deck import Deck, build_card_lines
from turn import TurnManager
from ai import ai_move
import termcolor as tc
def card_value(card):
    if card.rank in ['J', 'Q', 'K']:
        return 10
    elif card.rank == 'A':
        return 11  # We'll handle Ace flexibility later
    else:
        return int(card.rank)

def hand_value(hand):
    value = sum(card_value(c) for c in hand)
    # Adjust for Aces
    aces = sum(1 for c in hand if c.rank == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def print_hand(player, hand):
    print(f"{player}'s hand:")
    card_lines = [build_card_lines(card) for card in hand]
    for line_index in range(3):
        print("".join(card[line_index] for card in card_lines))
    print(f"= {hand_value(hand)}\n")

def print_single_card(player, card):
    print(f"{player}'s upcard:")
    card_lines = build_card_lines(card)
    for line_index in range(3):
        print(card_lines[line_index])
    print("\n")


def blackjack_game():
    players = ["Player", "Dealer"]
    turns = TurnManager(players)
    deck = Deck()
    deck.shuffle()
    hands = {}
    print("=" * 40)
    print("Welcome to Blackjack!")
    print("=" * 40)
    for player in players:
        hands[player] = [deck.draw(), deck.draw()]        
    upcard = hands["Dealer"][0] 

    # Player's turn
    while hand_value(hands["Player"]) < 21:
        print_single_card("Dealer", upcard) # Show dealer's upcard first
        print_hand("Player", hands["Player"]) # Then show player's hand

        while True:
            move = input("Hit or Stand? ").strip().lower()
            if move in ["hit", "stand"]:
                break
            print("Invalid input. Please type 'hit' or 'stand'.")
        if move == "hit":
            hands["Player"].append(deck.draw())
        else:
            break
        print("=" * 40)
    # AI (Dealer) decision loop
    while True:
        # ai_move function likely expects the actual upcard, not the full hand
        # Assuming ai_move handles a single card for upcard parameter correctly
        move = ai_move(hands["Dealer"], upcard)
        print(f"Dealer chooses to {move}")
        if move == "hit" or move == "double":
            hands["Dealer"].append(deck.draw())
            if move == "double":
                break
        else:
            break
    print("=" * 40)
    # Final hands
    print_hand("Player", hands["Player"])
    print_hand("Dealer", hands["Dealer"])
    print("=" * 40)
    # Determine winner
    player_score = hand_value(hands["Player"])
    dealer_score = hand_value(hands["Dealer"])

    if player_score > 21:
        print("Player busts! Dealer wins.")
    elif dealer_score > 21: # Dealer busts
        print("Player wins!")
    elif player_score > dealer_score:
        print("Player wins!")
    elif player_score == dealer_score:
        print("Push!")
    else: # dealer_score > player_score (and player didn't bust)
        print("Dealer wins.")
    print("=" * 40)
    if input("Play again? (y/n): ").strip().lower() == "y":
        blackjack_game()
# Demo: Print a single card using both functions
if __name__ == "__main__":
    blackjack_game()