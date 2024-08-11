import matplotlib.pyplot as plt
from collections import defaultdict
from mersenne_twister import MersenneTwister  # Assuming the previous code is saved as mersenne_twister.py

def verify_uniformity(rng, num_samples=1000000, num_bins=100):
    samples = [rng.random() for _ in range(num_samples)]
    plt.figure(figsize=(10, 6))
    plt.hist(samples, bins=num_bins, edgecolor='black')
    plt.title(f'Distribution of {num_samples} random numbers')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.show()

    # Chi-square test for uniformity
    expected_freq = num_samples / num_bins
    observed_freq = plt.hist(samples, bins=num_bins)[0]
    chi_square = sum((obs - expected_freq) ** 2 / expected_freq for obs in observed_freq)
    print(f"Chi-square statistic: {chi_square}")
    print("Lower chi-square values indicate better uniformity.")

def verify_periodicity(rng, sequence_length=1000000):
    sequence = [rng.random() for _ in range(sequence_length)]
    
    # Check for exact repetitions
    seen = defaultdict(list)
    for i, num in enumerate(sequence):
        if len(seen[num]) > 0:
            print(f"Exact repetition found at indices: {seen[num][0]} and {i}")
            return
        seen[num].append(i)
    
    print(f"No exact repetitions found in a sequence of {sequence_length} numbers.")

    # Analyze autocorrelation
    autocorrelation = [sum((sequence[i] - 0.5) * (sequence[i+lag] - 0.5) for i in range(len(sequence)-lag)) / (len(sequence)-lag) for lag in range(1, 101)]
    
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 101), autocorrelation)
    plt.title('Autocorrelation of the random sequence')
    plt.xlabel('Lag')
    plt.ylabel('Autocorrelation')
    plt.show()

# Run verification
rng = MersenneTwister()
verify_uniformity(rng)
verify_periodicity(rng)
