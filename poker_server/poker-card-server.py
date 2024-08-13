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

class MersenneTwister:
    def __init__(self, seed=None):
        self.w, self.n, self.m, self.r = 32, 624, 397, 31
        self.a = 0x9908B0DF
        self.u, self.d = 11, 0xFFFFFFFF
        self.s, self.b = 7, 0x9D2C5680
        self.t, self.c = 15, 0xEFC60000
        self.l = 18
        self.f = 1812433253

        self.MT = [0] * self.n
        self.index = self.n + 1
        self.lower_mask = (1 << self.r) - 1
        self.upper_mask = ~self.lower_mask

        if seed is None:
            seed = int(time.time())
        self.seed_mt(seed)

    def seed_mt(self, seed):
        self.MT[0] = seed
        for i in range(1, self.n):
            self.MT[i] = (self.f * (self.MT[i-1] ^ (self.MT[i-1] >> (self.w-2))) + i) & 0xffffffff
        self.twist()

    def extract_number(self):
        if self.index >= self.n:
            self.twist()

        y = self.MT[self.index]
        y = y ^ ((y >> self.u) & self.d)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        y = y ^ (y >> self.l)

        self.index += 1
        return y & 0xffffffff

    def twist(self):
        for i in range(self.n):
            x = (self.MT[i] & self.upper_mask) + (self.MT[(i+1) % self.n] & self.lower_mask)
            xA = x >> 1
            if x % 2 != 0:
                xA = xA ^ self.a
            self.MT[i] = self.MT[(i + self.m) % self.n] ^ xA
        self.index = 0

    def randint(self, a, b):
        range_size = b - a + 1
        if range_size <= 0:
            raise ValueError("Invalid range")
        
        bits_needed = (range_size - 1).bit_length()
        mask = (1 << bits_needed) - 1
        
        while True:
            value = self.extract_number() & mask
            if value < range_size:
                return a + value

class PokerCardHandler(BaseHTTPRequestHandler):
    advanced_rng = AdvancedRandomGenerator()
    mersenne_twister = MersenneTwister(advanced_rng.generate_numbers(0, 2**32 - 1, 1)[0])
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/draw':
            query_components = parse_qs(parsed_path.query)
            num_cards = int(query_components.get('count', [5])[0])  # Default to 5 if not specified
            
            card_indices = [self.mersenne_twister.randint(0, 51) for _ in range(num_cards)]
            
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