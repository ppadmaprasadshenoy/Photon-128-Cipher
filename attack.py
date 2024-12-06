import random
import time
from collections import defaultdict

STATE_SIZE = 256
BLOCK_SIZE = 128
OUTPUT_SIZE = 128

def rotate(x, r):
    return ((x << r) | (x >> (32 - r))) & 0xFFFFFFFF

def photon128_transform(state, block):
    for i in range(4):
        state[i] ^= block[i]
        state[i] = rotate(state[i], 7) ^ state[(i + 1) % 4]
    return state

def photon128_init():
    return [0] * 4

def photon128_absorb(state, message):
    padded_message = message + b'\x00' * (BLOCK_SIZE // 8 - len(message) % (BLOCK_SIZE // 8)) \
                     if len(message) % (BLOCK_SIZE // 8) != 0 else message
    
    for i in range(0, len(padded_message), BLOCK_SIZE // 8):
        block = [0] * 4
        for j in range(4):
            if i + j * 4 + 3 < len(padded_message):
                block[j] = (padded_message[i + j * 4] << 24) | \
                          (padded_message[i + j * 4 + 1] << 16) | \
                          (padded_message[i + j * 4 + 2] << 8) | \
                          padded_message[i + j * 4 + 3]
        state = photon128_transform(state, block)
    return state

def photon128_squeeze(state):
    hash_value = b""
    for i in range(4):
        hash_value += state[i].to_bytes(4, byteorder='big')
    return hash_value[:OUTPUT_SIZE // 8]

def photon128(message):
    state = photon128_init()
    state = photon128_absorb(state, message)
    return photon128_squeeze(state)

def analyze_preimage_resistance(orig_message, orig_hash):
    print("\nAttempting to find a preimage...")
    
    start_time = time.time()
    while time.time() - start_time < 30:
        test_len = random.randint(len(orig_message) - 5, len(orig_message) + 5)
        test_message = bytes(random.getrandbits(8) for _ in range(test_len))
        
        if test_message == orig_message:
            continue
            
        test_hash = photon128(test_message)
        
        if test_hash == orig_hash:
            print("Warning: First preimage found!")
            return False
    
    print("No preimage found")
    return True

def analyze_second_preimage_resistance(orig_message, orig_hash):
    print("\nAttempting to find a second preimage...")
    
    start_time = time.time()
    while time.time() - start_time < 30:
        test_message = bytearray(orig_message)
        num_modifications = random.randint(1, max(1, len(test_message)//2))
        for _ in range(num_modifications):
            pos = random.randint(0, len(test_message)-1)
            test_message[pos] = random.randint(0, 255)
        
        if bytes(test_message) == orig_message:
            continue
            
        test_hash = photon128(bytes(test_message))
        
        if test_hash == orig_hash:
            print("Warning: Second preimage found!")
            return False
    
    print("No second preimage found")
    return True

def analyze_collision_resistance(input_message):
    print("\nAttempting to find hash collisions...")
    
    original_hash = photon128(input_message)
    seen_hashes = defaultdict(list)
    seen_hashes[original_hash].append(input_message)
    
    start_time = time.time()
    while time.time() - start_time < 30:
        test_message = bytearray(input_message)
        num_modifications = random.randint(1, max(1, len(test_message)//2))
        for _ in range(num_modifications):
            pos = random.randint(0, len(test_message)-1)
            test_message[pos] = random.randint(0, 255)
        
        test_message = bytes(test_message)
        if test_message == input_message:
            continue
            
        test_hash = photon128(test_message)
        
        if test_hash in seen_hashes:
            for prev_message in seen_hashes[test_hash]:
                if prev_message != test_message:
                    print("Warning: Collision found!")
                    return False
        
        seen_hashes[test_hash].append(test_message)
    
    print("No collisions found")
    return True

def run_security_analysis(message):
    original_hash = photon128(message)
    
    print("\n=== Security Analysis Results ===")
    print(f"Message: {message.decode('utf-8', errors='replace')}")
    print(f"Hash: {original_hash.hex()}")
    
    results = {
        "First Preimage Resistance": analyze_preimage_resistance(message, original_hash),
        "Second Preimage Resistance": analyze_second_preimage_resistance(message, original_hash),
        "Collision Resistance": analyze_collision_resistance(message)
    }
    
    print("\n=== Summary ===")
    for test, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test}: {status}")
    
    all_passed = all(results.values())
    print("\nOverall Assessment:", "STRONG" if all_passed else "REQUIRES IMPROVEMENT")
    return all_passed

def main():
    while True:
        print("\n=== Photon-128 Hash Function ===")
        print("1. Hash a message")
        print("2. Run security analysis")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            message = input("Enter message to hash: ").encode('utf-8')
            hash_value = photon128(message)
            print(f"Hash: {hash_value.hex()}")
        
        elif choice == "2":
            message = input("Enter message for security analysis: ").encode('utf-8')
            run_security_analysis(message)
        
        elif choice == "3":
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()