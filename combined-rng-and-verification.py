import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from collections import defaultdict
import seaborn as sns

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
            seed = int(time.time() * 1000)
        self.seed_mt(seed)

    def seed_mt(self, seed):
        self.MT[0] = seed
        for i in range(1, self.n):
            self.MT[i] = (self.f * (self.MT[i-1] ^ (self.MT[i-1] >> (self.w-2))) + i) & 0xffffffff

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

def verify_uniformity(rng, num_samples=1000000, num_bins=100):
    samples = np.array([rng.random() for _ in range(num_samples)])
    
    # Create a figure with a 2x2 grid
    fig = plt.figure(figsize=(20, 20))
    gs = fig.add_gridspec(2, 2)
    
    # Enhanced histogram
    ax1 = fig.add_subplot(gs[0, :])
    counts, bins, patches = ax1.hist(samples, bins=num_bins, edgecolor='black', density=True, alpha=0.7)
    ax1.set_title(f'Distribution of {num_samples} Random Numbers', fontsize=16)
    ax1.set_xlabel('Value', fontsize=12)
    ax1.set_ylabel('Density', fontsize=12)
    
    # Add percentage labels to bars
    bin_centers = (bins[:-1] + bins[1:]) / 2
    for count, x, patch in zip(counts, bin_centers, patches):
        percentage = count * 100 / num_samples
        ax1.annotate(f'{percentage:.2f}%', 
                     (x, count), 
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom',
                     rotation=90, fontsize=8)
    
    # Add the ideal uniform distribution line
    ax1.axhline(y=1, color='r', linestyle='--', label='Ideal Uniform')
    ax1.legend(fontsize=10)
    
    # Residual plot
    ax2 = fig.add_subplot(gs[1, 0])
    residuals = counts - 1  # Difference from ideal uniform density
    ax2.bar(bin_centers, residuals, width=(bins[1]-bins[0]), color='g', alpha=0.6)
    ax2.set_title('Residuals (Difference from Ideal Uniform Distribution)', fontsize=16)
    ax2.set_xlabel('Value', fontsize=12)
    ax2.set_ylabel('Residual', fontsize=12)
    ax2.axhline(y=0, color='r', linestyle='--')
    
    # Add Q-Q plot
    ax3 = fig.add_subplot(gs[1, 1])
    stats.probplot(samples, dist="uniform", plot=ax3)
    ax3.set_title("Q-Q Plot", fontsize=16)
    
    # Add summary statistics
    textstr = '\n'.join((
        f'Mean: {np.mean(samples):.6f}',
        f'Std Dev: {np.std(samples):.6f}',
        f'Median: {np.median(samples):.6f}',
        f'Min: {np.min(samples):.6f}',
        f'Max: {np.max(samples):.6f}',
        f'Skewness: {stats.skew(samples):.6f}',
        f'Kurtosis: {stats.kurtosis(samples):.6f}'
    ))
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=10,
             verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.show()
    
    # Kernel Density Estimation plot
    plt.figure(figsize=(12, 6))
    sns.kdeplot(samples, shade=True)
    plt.title('Kernel Density Estimation of Random Numbers', fontsize=16)
    plt.xlabel('Value', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.show()

    # Statistical tests
    print("\nUniformity Tests:")
    
    # Chi-square test
    observed_freq, _ = np.histogram(samples, bins=num_bins)
    expected_freq = num_samples / num_bins
    chi_square_stat, p_value = stats.chisquare(observed_freq)
    print(f"Chi-square test: statistic={chi_square_stat:.4f}, p-value={p_value:.4f}")
    
    # Kolmogorov-Smirnov test
    ks_statistic, ks_p_value = stats.kstest(samples, 'uniform')
    print(f"Kolmogorov-Smirnov test: statistic={ks_statistic:.4f}, p-value={ks_p_value:.4f}")
    
    # Anderson-Darling test
    ad_result = stats.anderson(samples, dist='uniform')
    print(f"Anderson-Darling test: statistic={ad_result.statistic:.4f}")
    print("Critical values:", ", ".join([f"{value:.4f} at {percent}%" for value, percent in zip(ad_result.critical_values, ad_result.significance_level)]))

    # Shapiro-Wilk test
    sw_statistic, sw_p_value = stats.shapiro(samples[:5000])  # Limited to 5000 samples due to computational constraints
    print(f"Shapiro-Wilk test: statistic={sw_statistic:.4f}, p-value={sw_p_value:.4f}")

def verify_periodicity(rng, sequence_length=1000000, max_lag=1000):
    sequence = np.array([rng.random() for _ in range(sequence_length)])
    
    print("\nPeriodicity Analysis:")
    
    # Check for exact repetitions
    seen = defaultdict(list)
    for i, num in enumerate(sequence):
        if len(seen[num]) > 0:
            print(f"Exact repetition found at indices: {seen[num][0]} and {i}")
            break
        seen[num].append(i)
    else:
        print(f"No exact repetitions found in a sequence of {sequence_length} numbers.")
    
    # Autocorrelation
    autocorr = np.correlate(sequence - sequence.mean(), sequence - sequence.mean(), mode='full')
    autocorr = autocorr[len(autocorr)//2:] / (sequence.var() * np.arange(len(sequence), 0, -1))
    
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, max_lag + 1), autocorr[1:max_lag+1])
    plt.title('Autocorrelation of the random sequence')
    plt.xlabel('Lag')
    plt.ylabel('Autocorrelation')
    plt.axhline(y=0, color='r', linestyle='--')
    
    # Add confidence intervals
    conf_int = 1.96 / np.sqrt(len(sequence))
    plt.axhline(y=conf_int, color='g', linestyle='--', label='95% Confidence Interval')
    plt.axhline(y=-conf_int, color='g', linestyle='--')
    plt.legend()
    
    plt.show()
    
    # Runs test
    median = np.median(sequence)
    runs = np.diff(np.sign(sequence - median) != 0).sum() + 1
    n1 = np.sum(sequence > median)
    n2 = len(sequence) - n1
    
    runs_mean = (2 * n1 * n2) / (n1 + n2) + 1
    runs_var = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2)**2 * (n1 + n2 - 1))
    z_score = (runs - runs_mean) / np.sqrt(runs_var)
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    
    print("\nRuns Test for Independence:")
    print(f"Number of runs: {runs}")
    print(f"Z-score: {z_score:.4f}")
    print(f"P-value: {p_value:.4f}")

# Run verification
if __name__ == "__main__":
    rng = MersenneTwister()
    verify_uniformity(rng)
    verify_periodicity(rng)