import time

class TurnManager:
    def __init__(self, players):
        self.players = players
        self.current_index = 0
        self.start_time = time.time()

    def current_player(self):
        return self.players[self.current_index]

    def next_turn(self):
        self.current_index = (self.current_index + 1) % len(self.players)
        self.start_time = time.time()

    def turn_duration(self):
        return time.time() - self.start_time