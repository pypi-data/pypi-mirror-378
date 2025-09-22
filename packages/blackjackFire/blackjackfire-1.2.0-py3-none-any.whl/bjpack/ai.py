def card_value(card):
    if card.rank in ['J', 'Q', 'K']:
        return 10
    elif card.rank == 'A':
        return 11
    else:
        return int(card.rank)

def hand_value(hand):
    value = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c.rank == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def is_soft(hand):
    return any(c.rank == 'A' for c in hand) and hand_value(hand) <= 21

def ai_move(hand, dealer_upcard):
    dealer = dealer_upcard.rank
    total = hand_value(hand)

    if is_soft(hand) and len(hand) == 2:
        return soft_strategy(total, dealer)
    else:
        return hard_strategy(total, dealer)

def soft_strategy(total, dealer):
    if total == 20:
        return "stand"
    if total == 19:
        return "double" if dealer == '6' else "stand"
    if total == 18:
        if dealer in ['2', '3', '4', '5', '6']:
            return "double"
        elif dealer in ['9', '10', 'J', 'Q', 'K', 'A']:
            return "hit"
        else:
            return "stand"
    if total == 17:
        return "double" if dealer in ['3', '4', '5', '6'] else "hit"
    if total in [15, 16]:
        return "double" if dealer in ['4', '5', '6'] else "hit"
    if total in [13, 14]:
        return "double" if dealer in ['5', '6'] else "hit"
    return "hit"

def hard_strategy(total, dealer):
    if total >= 17:
        return "stand"
    if total in [13, 14, 15, 16]:
        return "stand" if dealer in ['2', '3', '4', '5', '6'] else "hit"
    if total == 12:
        return "stand" if dealer in ['4', '5', '6'] else "hit"
    if total == 11:
        return "double"
    if total == 10:
        return "double" if dealer in ['2', '3', '4', '5', '6', '7', '8', '9'] else "hit"
    if total == 9:
        return "double" if dealer in ['3', '4', '5', '6'] else "hit"
    return "hit"