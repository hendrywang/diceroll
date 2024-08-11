import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import hashlib
import os
import random
import numpy as np

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

class PokerCardHandler(BaseHTTPRequestHandler):
    random_generator = AdvancedRandomGenerator()
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def do_GET(self):
        if self.path == '/draw':
            num_cards = 5  # Number of cards to draw
            card_indices = self.random_generator.generate_numbers(0, 51, num_cards)
            
            cards = []
            for index in card_indices:
                suit = self.suits[index // 13]
                value = self.values[index % 13]
                cards.append({'suit': suit, 'value': value})
            
            response = {'cards': cards}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
        self.end_headers()

def run_server(port=3040):
    server_address = ('', port)
    httpd = HTTPServer(server_address, PokerCardHandler)
    print(f'Server running on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
