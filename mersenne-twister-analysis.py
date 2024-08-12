import time
import os
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import itertools

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
            seed = int(time.time_ns())
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

    def random(self):
        return self.extract_number() / 0xffffffff

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

def generate_seed():
    return int.from_bytes(time.time_ns().to_bytes(8, 'little') + os.urandom(8), 'little')

def analyze_distribution(numbers, num_bins):
    counts, _ = np.histogram(numbers, bins=num_bins, range=(1, num_bins+1))
    
    print("\nNumber Distribution:")
    print("Number | Count | Percentage")
    print("-" * 30)
    for i, count in enumerate(counts, 1):
        percentage = count / len(numbers) * 100
        print(f"{i:6d} | {count:5d} | {percentage:6.2f}%")
    
    ks_statistic, p_value = stats.kstest(numbers, 'uniform', args=(0.5, num_bins+0.5))
    
    print(f"\nKolmogorov-Smirnov test:")
    print(f"KS statistic: {ks_statistic:.4f}")
    print(f"p-value: {p_value:.4f}")
    print("Note: For a uniform distribution, the p-value should be greater than 0.05.")

def plot_distribution(numbers, num_bins):
    plt.figure(figsize=(16, 12))
    plt.suptitle('Analysis of Generated Numbers', fontsize=16)

    plt.subplot(2, 2, 1)
    plt.hist(numbers, bins=num_bins, range=(1, num_bins+1), align='left', rwidth=0.8)
    plt.title('Distribution of Generated Numbers')
    plt.xlabel('Number')
    plt.ylabel('Frequency')
    plt.xticks(range(1, num_bins + 1, 4))
    plt.grid(axis='y', alpha=0.75)

    plt.subplot(2, 2, 2)
    stats.probplot(numbers, dist=stats.uniform, sparams=(0.5, num_bins), plot=plt)
    plt.title('Probability Plot')

    plt.subplot(2, 2, 3)
    sns.kdeplot(numbers, fill=True)  # Changed 'shade' to 'fill'
    plt.title('Kernel Density Estimation')
    plt.xlabel('Number')
    plt.ylabel('Density')

    plt.subplot(2, 2, 4)
    autocorr = [pd.Series(numbers).autocorr(lag=i) for i in range(1, 51)]
    plt.plot(range(1, 51), autocorr)
    plt.title('Autocorrelation Plot')
    plt.xlabel('Lag')
    plt.ylabel('Autocorrelation')

    plt.tight_layout()
    plt.show()

def plot_2d_distribution(numbers, num_bins):
    plt.figure(figsize=(12, 10))
    plt.suptitle('2D Distribution Analysis', fontsize=16)

    plt.subplot(2, 1, 1)
    plt.hist2d(numbers[:-1], numbers[1:], bins=num_bins, range=[[0.5, num_bins+0.5], [0.5, num_bins+0.5]])
    plt.colorbar(label='Frequency')
    plt.title('2D Histogram of Consecutive Numbers')
    plt.xlabel('Number n')
    plt.ylabel('Number n+1')

    plt.subplot(2, 1, 2)
    plt.scatter(numbers[:-1], numbers[1:], alpha=0.1)
    plt.title('Scatter Plot of Consecutive Numbers')
    plt.xlabel('Number n')
    plt.ylabel('Number n+1')

    plt.tight_layout()
    plt.show()

def analyze_runs(numbers, num_bins):
    runs = [len(list(group)) for key, group in itertools.groupby(numbers)]
    
    plt.figure(figsize=(12, 6))
    plt.suptitle('Run Length Analysis', fontsize=16)

    plt.subplot(1, 2, 1)
    plt.hist(runs, bins=20)
    plt.title('Distribution of Run Lengths')
    plt.xlabel('Run Length')
    plt.ylabel('Frequency')

    plt.subplot(1, 2, 2)
    sns.boxplot(y=runs)
    plt.title('Box Plot of Run Lengths')
    plt.ylabel('Run Length')

    plt.tight_layout()
    plt.show()

# Main execution
seed = generate_seed()
print(f"Generated seed: {seed}")

rng = MersenneTwister(seed)

num_samples = 1000000
num_bins = 52

generated_numbers = [rng.randint(1, num_bins) for _ in range(num_samples)]

analyze_distribution(generated_numbers, num_bins)
plot_distribution(generated_numbers, num_bins)
plot_2d_distribution(generated_numbers, num_bins)
analyze_runs(generated_numbers, num_bins)