const http = require('http');
const crypto = require('crypto');
const url = require('url');
const querystring = require('querystring');

class AdvancedRandomGenerator {
    constructor() {
        this.reseed();
    }

    reseed() {
        const seedSources = [
            crypto.randomBytes(4).readUInt32BE(0),
            Date.now(),
            crypto.randomBytes(4).readUInt32BE(0),
            this.hashCode(JSON.stringify(this.state))
        ];
        const seed = crypto.createHash('sha512').update(seedSources.toString()).digest();
        this.state = new Uint32Array(seed.buffer, 0, 4);
    }

    hashCode(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return hash;
    }

    generateNumbers(minValue, maxValue, count) {
        const extra = Math.max(100, count);
        const numbers = new Array(count + extra).fill(0).map(() => 
            Math.floor(this.state[0] / 0x100000000 * (maxValue - minValue + 1) + minValue)
        );

        for (let i = numbers.length - 1; i > 0; i--) {
            const j = Math.floor(this.state[0] / 0x100000000 * (i + 1));
            [numbers[i], numbers[j]] = [numbers[j], numbers[i]];
        }

        const result = numbers.slice(0, count);
        this.reseed();
        return result;
    }
}

class MersenneTwister {
    constructor(seed = null) {
        this.w = 32;
        this.n = 624;
        this.m = 397;
        this.r = 31;
        this.a = 0x9908B0DF;
        this.u = 11;
        this.d = 0xFFFFFFFF;
        this.s = 7;
        this.b = 0x9D2C5680;
        this.t = 15;
        this.c = 0xEFC60000;
        this.l = 18;
        this.f = 1812433253;

        this.MT = new Array(this.n).fill(0);
        this.index = this.n + 1;
        this.lowerMask = (1 << this.r) - 1;
        this.upperMask = ~this.lowerMask >>> 0;

        this.seedMt(seed || Date.now());
    }

    seedMt(seed) {
        this.MT[0] = seed >>> 0;
        for (let i = 1; i < this.n; i++) {
            this.MT[i] = (this.f * (this.MT[i-1] ^ (this.MT[i-1] >>> (this.w-2))) + i) >>> 0;
        }
        this.twist();
    }

    extractNumber() {
        if (this.index >= this.n) {
            this.twist();
        }

        let y = this.MT[this.index];
        y = y ^ ((y >>> this.u) & this.d);
        y = y ^ ((y << this.s) & this.b);
        y = y ^ ((y << this.t) & this.c);
        y = y ^ (y >>> this.l);

        this.index++;
        return y >>> 0;
    }

    twist() {
        for (let i = 0; i < this.n; i++) {
            const x = (this.MT[i] & this.upperMask) + (this.MT[(i+1) % this.n] & this.lowerMask);
            let xA = x >>> 1;
            if (x % 2 !== 0) {
                xA = xA ^ this.a;
            }
            this.MT[i] = this.MT[(i + this.m) % this.n] ^ xA;
        }
        this.index = 0;
    }

    randint(a, b) {
        const rangeSize = b - a + 1;
        if (rangeSize <= 0) {
            throw new Error("Invalid range");
        }
        
        const bitsNeeded = (rangeSize - 1).toString(2).length;
        const mask = (1 << bitsNeeded) - 1;
        
        while (true) {
            const value = this.extractNumber() & mask;
            if (value < rangeSize) {
                return a + value;
            }
        }
    }
}

const advancedRng = new AdvancedRandomGenerator();
const mersenneTwister = new MersenneTwister(advancedRng.generateNumbers(0, 2**32 - 1, 1)[0]);
const suits = ['hearts', 'diamonds', 'clubs', 'spades'];
const values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url);
    
    if (req.method === 'OPTIONS') {
        res.writeHead(200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'X-Requested-With'
        });
        res.end();
        return;
    }

    if (parsedUrl.pathname === '/draw') {
        const query = querystring.parse(parsedUrl.query);
        const numCards = parseInt(query.count) || 5;

        const cardIndices = Array.from({length: numCards}, () => mersenneTwister.randint(0, 51));

        const cards = cardIndices.map(index => ({
            suit: suits[Math.floor(index / 13)],
            value: values[index % 13]
        }));

        const response = { cards };

        res.writeHead(200, {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        });
        res.end(JSON.stringify(response));
    } else {
        res.writeHead(404);
        res.end();
    }
});

const PORT = 3040;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
