import secrets
from collections import Counter
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
        results.append(tuple(generate_secure_random_number(1, 6) for _ in range(3)))
    return results

def compare_rolls(rolls1, rolls2):
    same_results = []
    for r1, r2 in zip(rolls1, rolls2):
        if r1 == r2:
            same_results.append(r1)
    return same_results

def print_comparison_results(same_results, total_rolls):
    print(f"\nTotal rolls: {total_rolls}")
    print(f"Number of matching results: {len(same_results)}")
    print(f"Percentage of matching results: {len(same_results) / total_rolls * 100:.2f}%")
    
    print("\nMatching results:")
    print("Roll | Count | Percentage")
    print("-----|-------|------------")
    
    result_counter = Counter(same_results)
    for roll, count in sorted(result_counter.items()):
        percentage = count / len(same_results) * 100
        print(f"{roll} | {count:5d} | {percentage:.2f}%")

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

if __name__ == "__main__":
    print("Welcome to the Double Dice Roll Comparator!")
    num_rolls = get_valid_input()
    
    print(f"\nSimulating {num_rolls} rolls of three dice, twice...")
    
    rolls1 = simulate_dice_rolls(num_rolls)
    print("\nFirst set of rolls completed.")
    
    rolls2 = simulate_dice_rolls(num_rolls)
    print("\nSecond set of rolls completed.")
    
    print("\nComparing the results...")
    same_results = compare_rolls(rolls1, rolls2)
    
    print_comparison_results(same_results, num_rolls)
