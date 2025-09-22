from bjpack.deck import Deck, build_card_lines
from bjpack.turn import TurnManager
from bjpack.ai import ai_move

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

def blackjack_game():
    players = ["Player", "Dealer"]
    turns = TurnManager(players)
    deck = Deck()
    deck.shuffle()

    hands = {player: [deck.draw(), deck.draw()] for player in players}

    # Player's turn
    while hand_value(hands["Player"]) < 21:
        print_hand("Player", hands["Player"])
        while True:
            move = input("Hit or Stand? ").strip().lower()
            if move in ["hit", "stand"]:
                break
            print("Invalid input. Please type 'hit' or 'stand'.")
        if move == "hit":
            hands["Player"].append(deck.draw())
        else:
            break

    # Dealer's turn

    # Dealer's upcard
    dealer_upcard = hands["Dealer"][0]

    # AI (Dealer) decision loop
    while True:
        move = ai_move(hands["Dealer"], dealer_upcard)
        print(f"Dealer chooses to {move}")
        if move == "hit" or move == "double":
            hands["Dealer"].append(deck.draw())
            if move == "double":
                break
        else:
            break

    # Final hands
    print_hand("Player", hands["Player"])
    print_hand("Dealer", hands["Dealer"])

    # Determine winner
    player_score = hand_value(hands["Player"])
    dealer_score = hand_value(hands["Dealer"])

    if player_score > 21:
        print("Player busts! Dealer wins.")
    elif dealer_score > 21 or player_score > dealer_score:
        print("Player wins!")
    elif player_score == dealer_score:
        print("Push!")
    else:
        print("Dealer wins.")

    if input("Play again? (y/n): ").strip().lower() == "y":
        blackjack_game()

