import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import hashlib
import os
import random
import numpy as np
from urllib.parse import urlparse, parse_qs

class AdvancedRandomGenerator:
    def __init__(self):
        self.numpy_rng = np.random.RandomState()
        self.reseed()

    def reseed(self):
        seed_sources = [
            int.from_bytes(os.urandom(4), 'big'),
            int(time.time() * 1000000),
            int.from_bytes(secrets.token_bytes(4), 'big'),
            hash(str(self.numpy_rng.get_state()))
        ]
        seed = hashlib.sha512(str(seed_sources).encode()).digest()
        seed_int = int.from_bytes(seed[:4], 'big')
        self.numpy_rng.seed(seed_int)

    def generate_numbers(self, min_value, max_value, count):
        extra = max(100, count)
        numbers = self.numpy_rng.randint(min_value, max_value + 1, size=count + extra)
        
        for i in range(len(numbers) - 1, 0, -1):
            j = self.numpy_rng.randint(0, i + 1)
            numbers[i], numbers[j] = numbers[j], numbers[i]
        
        result = numbers[:count].tolist()
        self.reseed()
        return result

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def to_dict(self):
        return {"suit": self.suit, "value": self.value}

class DeckManager:
    def __init__(self, num_decks):
        self.num_decks = num_decks
        self.reset_decks()

    def reset_decks(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, value) for _ in range(self.num_decks) for suit in suits for value in values]
        self.shuffle()

    def shuffle(self):
        for i in range(len(self.cards)):
            j = secrets.randbelow(i + 1)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def draw_cards(self, num_cards):
        drawn_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:] + drawn_cards  # Move drawn cards to the end
        self.shuffle()  # Reshuffle after each draw
        return drawn_cards

    def cards_remaining(self):
        return len(self.cards)

class PokerCardHandler(BaseHTTPRequestHandler):
    deck_manager = None

    @classmethod
    def initialize_deck_manager(cls, num_decks):
        cls.deck_manager = DeckManager(num_decks)

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/draw':
            self.handle_draw_request(parsed_path)
        elif parsed_path.path == '/reset':
            self.handle_reset_request(parsed_path)
        else:
            self.send_error(404)

    def handle_draw_request(self, parsed_path):
        query_components = parse_qs(parsed_path.query)
        num_cards = int(query_components.get('count', [5])[0])  # Default to 5 if not specified

        drawn_cards = self.deck_manager.draw_cards(num_cards)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()

        response = {
            'cards': [card.to_dict() for card in drawn_cards],
            'cards_remaining': self.deck_manager.cards_remaining()
        }

        self.wfile.write(json.dumps(response).encode())

    def handle_reset_request(self, parsed_path):
        query_components = parse_qs(parsed_path.query)
        num_decks = int(query_components.get('decks', [1])[0])  # Default to 1 if not specified
        
        self.initialize_deck_manager(num_decks)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        response = {
            'message': f'Deck reset successful. Using {num_decks} deck(s).',
            'cards_remaining': self.deck_manager.cards_remaining()
        }
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

def run_server(port=3040):
    PokerCardHandler.initialize_deck_manager(1)  # Start with 1 deck by default
    server_address = ('', port)
    httpd = HTTPServer(server_address, PokerCardHandler)
    print(f'Server running on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()