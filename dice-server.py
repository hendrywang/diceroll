import http.server
import socketserver
import json
import os
import time
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class FortunaGenerator:
    def __init__(self):
        self.key = os.urandom(32)
        self.counter = 0
        self.last_reseed_time = 0
        self.reseed_interval = 10  # Reseed every 10 seconds

    def reseed(self):
        current_time = time.time()
        if current_time - self.last_reseed_time >= self.reseed_interval:
            self.key = hashlib.sha256(self.key + os.urandom(32)).digest()
            self.last_reseed_time = current_time

    def generate_block(self):
        self.counter += 1
        cipher = Cipher(algorithms.AES(self.key), modes.CTR(self.counter.to_bytes(16, 'big')), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(b'\x00' * 16) + encryptor.finalize()

    def generate(self, num_bytes):
        self.reseed()
        output = b""
        while len(output) < num_bytes:
            output += self.generate_block()
        return output[:num_bytes]

class DiceHandler(http.server.SimpleHTTPRequestHandler):
    fortuna = FortunaGenerator()  # Class-level Fortuna generator instance

    def do_GET(self):
        if self.path == '/roll':
            dice_values = [self.roll_die() for _ in range(3)]
            response = json.dumps({"dice": dice_values})
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # Allow CORS
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            self.send_error(404)

    @classmethod
    def roll_die(cls):
        random_bytes = cls.fortuna.generate(1)
        return (random_bytes[0] % 6) + 1

if __name__ == "__main__":
    PORT = 3344
    IP = os.environ.get('IP', '0.0.0.0')  # Get IP from environment variable, default to '0.0.0.0'
    Handler = DiceHandler
    with socketserver.TCPServer((IP, PORT), Handler) as httpd:
        print(f"Server running on {IP}:{PORT}")
        httpd.serve_forever()