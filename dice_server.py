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
        # Combine multiple entropy sources
        seed_sources = [
            int.from_bytes(os.urandom(4), 'big'),
            int(time.time() * 1000000),
            int.from_bytes(secrets.token_bytes(4), 'big'),
            hash(str(self.numpy_rng.get_state()))
        ]
        seed = hashlib.sha512(str(seed_sources).encode()).digest()
        # Use only the first 4 bytes (32 bits) of the hash for seeding
        seed_int = int.from_bytes(seed[:4], 'big')
        self.numpy_rng.seed(seed_int)

    def generate_numbers(self, min_value, max_value, count):
        # Generate more numbers than needed
        extra = max(100, count)
        numbers = self.numpy_rng.randint(min_value, max_value + 1, size=count + extra)
        
        # Perform Fisher-Yates shuffle
        for i in range(len(numbers) - 1, 0, -1):
            j = self.numpy_rng.randint(0, i + 1)
            numbers[i], numbers[j] = numbers[j], numbers[i]
        
        # Use the first 'count' numbers after shuffling
        result = numbers[:count].tolist()
        
        # Reseed after generating a batch of numbers
        self.reseed()
        
        return result

class DiceRollHandler(BaseHTTPRequestHandler):
    random_generator = AdvancedRandomGenerator()

    def do_GET(self):
        if self.path == '/roll':
            dice_results = self.random_generator.generate_numbers(1, 6, 3)
            total_sum = sum(dice_results)
            
            response = {
                'dice': dice_results,
                'sum': total_sum,
                'big_small': 'Big' if total_sum >= 11 else 'Small',
                'triple': all(d == dice_results[0] for d in dice_results)
            }
            
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

def run_server(port=3030):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DiceRollHandler)
    print(f'Server running on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()