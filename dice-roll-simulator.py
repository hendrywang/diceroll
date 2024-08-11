import secrets
from collections import Counter
import time
from tqdm import tqdm

def generate_secure_random_number(min_value, max_value):
    range_size = max_value - min_value + 1
    if range_size <= 0:
        raise ValueError("Invalid range")
    
    bits_needed = (range_size - 1).bit_length()
    mask = (1 << bits_needed) - 1
    
    while True:
        value = secrets.randbits(bits_needed) & mask
        if value < range_size:
            return min_value + value

def simulate_dice_rolls(num_rolls):
    results = []
    for _ in tqdm(range(num_rolls), desc="Simulating rolls", unit="roll"):
        results.extend([generate_secure_random_number(1, 6) for _ in range(3)])
    return results

def print_frequency_table(results):
    counts = Counter(results)
    print("\nIndividual Dice Frequency Table:")
    print("Number |   a   |   b   |   c   |  Total")
    print("-------|-------|-------|-------|--------")
    total_rolls = len(results) // 3
    for num in range(1, 7):
        a_count = sum(1 for i in range(0, len(results), 3) if results[i] == num)
        b_count = sum(1 for i in range(1, len(results), 3) if results[i] == num)
        c_count = sum(1 for i in range(2, len(results), 3) if results[i] == num)
        total_count = counts[num]
        print(f"{num:6} | {a_count:5} | {b_count:5} | {c_count:5} | {total_count:6} ({total_count/len(results)*100:.2f}%)")

    print(f"\nTotal rolls: {total_rolls}")
    expected = total_rolls * 3 / 6
    chi_square = sum((counts[i] - expected) ** 2 / expected for i in range(1, 7))
    print(f"Chi-square statistic: {chi_square:.4f}")

def count_triples(results):
    return sum(1 for i in range(0, len(results), 3) if results[i] == results[i+1] == results[i+2])

def count_specific_triples(results):
    triples_count = Counter()
    for i in range(0, len(results), 3):
        if results[i] == results[i+1] == results[i+2]:
            triples_count[results[i]] += 1
    return triples_count

def print_triples_stats(results):
    total_rolls = len(results) // 3
    triples = count_triples(results)
    triples_percentage = (triples / total_rolls) * 100
    
    print("\nTriples Statistics:")
    print(f"Total triples: {triples}")
    print(f"Percentage of rolls with triples: {triples_percentage:.2f}%")
    
    expected_triples_prob = 1 / 36
    expected_triples = total_rolls * expected_triples_prob
    print(f"Expected number of triples: {expected_triples:.2f}")
    print(f"Expected percentage: {expected_triples_prob * 100:.2f}%")

    specific_triples = count_specific_triples(results)
    print("\nBreakdown of specific triples:")
    print("Triple | Count | Percentage")
    print("-------|-------|------------")
    for num in range(1, 7):
        count = specific_triples[num]
        percentage = (count / total_rolls) * 100
        print(f"  {num}-{num}-{num}  | {count:5} | {percentage:.2f}%")

def calculate_sum_frequency(results):
    sum_counts = Counter()
    for i in range(0, len(results), 3):
        roll_sum = sum(results[i:i+3])
        sum_counts[roll_sum] += 1
    return sum_counts

def print_sum_frequency_table(results):
    total_rolls = len(results) // 3
    sum_counts = calculate_sum_frequency(results)
    
    print("\nSum of Three Dice Frequency Table:")
    print("Sum   | Count | Percentage")
    print("------|-------|------------")
    for roll_sum in range(3, 19):  # Sum of 3 dice ranges from 3 to 18
        count = sum_counts[roll_sum]
        percentage = (count / total_rolls) * 100
        print(f"{roll_sum:4} | {count:5} | {percentage:6.2f}%")

def print_big_small_table(results):
    total_rolls = len(results) // 3
    sum_counts = calculate_sum_frequency(results)
    
    small_count = sum(sum_counts[i] for i in range(3, 11))
    big_count = sum(sum_counts[i] for i in range(11, 19))
    
    print("\nBig and Small Counts:")
    print("Category | Count | Percentage")
    print("---------|-------|------------")
    print(f"Small (3-10) | {small_count:5} | {small_count/total_rolls*100:6.2f}%")
    print(f"Big (11-18) | {big_count:5} | {big_count/total_rolls*100:6.2f}%")

def get_valid_input():
    while True:
        try:
            num_rolls = int(input("Enter the number of times to roll the dice (1-1000000): "))
            if 1 <= num_rolls <= 1000000:
                return num_rolls
            else:
                print("Please enter a number between 1 and 1,000,000.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

# Main execution
if __name__ == "__main__":
    print("Welcome to the Comprehensive Dice Roll Simulator!")
    num_rolls = get_valid_input()
    
    print(f"\nSimulating {num_rolls} rolls of three dice (a, b, c)...")
    start_time = time.time()
    results = simulate_dice_rolls(num_rolls)
    end_time = time.time()

    print(f"\nSimulation completed!")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print_frequency_table(results)
    print_triples_stats(results)
    print_sum_frequency_table(results)
    print_big_small_table(results)