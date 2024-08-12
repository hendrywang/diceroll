import requests
import random

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 0
        self.is_bust = False

    def hit(self, card):
        self.hand.append(card)
        self.calculate_score()

    def calculate_score(self):
        self.score = 0
        ace_count = 0
        for card in self.hand:
            if card['value'] in ['J', 'Q', 'K']:
                self.score += 10
            elif card['value'] == 'A':
                ace_count += 1
            else:
                self.score += int(card['value'])
        
        for _ in range(ace_count):
            if self.score + 11 <= 21:
                self.score += 11
            else:
                self.score += 1
        
        if self.score > 21:
            self.is_bust = True

    def show_hand(self):
        return f"{self.name}'s hand: {', '.join([f'{card['value']} of {card['suit']}' for card in self.hand])} (Score: {self.score})"

class Banker(Player):
    def __init__(self):
        super().__init__("Banker")

    def show_initial_hand(self):
        return f"Banker's hand: {self.hand[0]['value']} of {self.hand[0]['suit']}, [Hidden]"

def draw_cards(num_cards):
    response = requests.get(f"http://localhost:3040/draw?count={num_cards}")
    if response.status_code == 200:
        return response.json()['cards']
    else:
        raise Exception("Failed to draw cards from the server")

def play_blackjack():
    players = [Player(f"Player {i+1}") for i in range(8)]
    banker = Banker()
    all_players = players + [banker]

    # Initial deal
    for _ in range(2):
        for player in all_players:
            card = draw_cards(1)[0]
            player.hit(card)

    # Show initial hands
    for player in players:
        print(player.show_hand())
    print(banker.show_initial_hand())

    # Players' turns
    for player in players:
        while player.score < 21:
            choice = input(f"{player.name}, do you want to hit or stand? (h/s): ").lower()
            if choice == 'h':
                card = draw_cards(1)[0]
                player.hit(card)
                print(player.show_hand())
                if player.is_bust:
                    print(f"{player.name} is bust!")
                    break
            elif choice == 's':
                break

    # Banker's turn
    print("\nBanker's turn:")
    print(banker.show_hand())
    while banker.score < 17:
        card = draw_cards(1)[0]
        banker.hit(card)
        print(banker.show_hand())

    # Determine winners
    print("\nFinal Results:")
    for player in players:
        if not player.is_bust:
            if banker.is_bust or player.score > banker.score:
                print(f"{player.name} wins!")
            elif player.score == banker.score:
                print(f"{player.name} ties with the Banker.")
            else:
                print(f"{player.name} loses.")
        else:
            print(f"{player.name} is bust and loses.")

    if not banker.is_bust:
        print(f"Banker's final hand: {banker.show_hand()}")
    else:
        print("Banker is bust!")

if __name__ == "__main__":
    play_blackjack()
