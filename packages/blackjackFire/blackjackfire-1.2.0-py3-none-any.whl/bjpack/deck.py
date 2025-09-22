import termcolor as tc
import random
from colorama import just_fix_windows_console
just_fix_windows_console()
class Card:
    suit_colors = {"♠": "cyan", "♥": "red", "♦": "magenta", "♣": "yellow"}

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.color = Card.suit_colors[suit]

    def __str__(self):
        return f"{self.rank}{self.suit}"

class DiscardPile:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def top_card(self):
        return self.cards[-1] if self.cards else None

class Deck:
    def __init__(self):
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.suits = ["♠", "♥", "♦", "♣"]
        self.cards = []
        self.discard_pile = DiscardPile()

        for suit in self.suits:
            for rank in self.ranks:
                self.cards.append(Card(rank, suit))

    def shuffle(self):
        random.shuffle(self.cards)

    def discard(self, card):
        self.discard_pile.add_card(card)

    def reshuffle_from_discard(self):
        if self.discard_pile.cards:
            self.cards = self.discard_pile.cards[:]
            self.discard_pile.cards.clear()
            self.shuffle()
            print("Deck was empty. Reshuffled from discard pile.")

    def draw(self):
        if not self.cards:
            self.reshuffle_from_discard()
        return self.cards.pop() if self.cards else None
def build_card_lines(card):
    card_str = str(card)
    color = card.color
    return [
        tc.colored("┌─────┐", color),
        tc.colored(f"│ {card_str:<3} │", color),
        tc.colored("└─────┘", color)
    ]
def print_deck(deck):
    cards_per_row = 13
    card_lines = [build_card_lines(card) for card in deck.cards]
    for i in range(0, len(card_lines), cards_per_row):
        row = card_lines[i:i+cards_per_row]
        for line_index in range(3):
            print("".join(card[line_index] for card in row))


# Demo: Print the deck
if __name__ == "__main__":
    deck_instance = Deck()
    deck_instance.shuffle()
    print_deck(deck_instance)
    input("\nPress Enter to exit...")