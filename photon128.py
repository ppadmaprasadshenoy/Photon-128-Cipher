STATE_SIZE = 144
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
    state = [0] * 4  
    return state

def photon128_absorb(state, message):
    padded_message = message + b'\x00' * (BLOCK_SIZE // 8 - len(message) % (BLOCK_SIZE // 8)) \
                     if len(message) % (BLOCK_SIZE // 8) != 0 else message

    for i in range(0, len(padded_message), BLOCK_SIZE // 8):
        block = [0] * 4
        for j in range(4):
            if i + j * 4 + 3 < len(padded_message):
                block[j] = (padded_message[i + j * 4] << 24) | (padded_message[i + j * 4 + 1] << 16) | \
                           (padded_message[i + j * 4 + 2] << 8) | padded_message[i + j * 4 + 3]
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

def main():
    message = input("Enter the message to hash: ").encode('utf-8')
    
    hash_value = photon128(message)
    
    print(f"Hash (Photon-128): {hash_value.hex()}")
    
    verify = input("Do you want to verify a message? (yes/y to verify, anything else to skip): ").strip().lower()
    
    if verify == "yes" or verify == "y":
        verify_message = input("Enter the message to verify: ").encode('utf-8')
        
        verify_hash = photon128(verify_message)
        
        if verify_hash == hash_value:
            print("The hash matches! The message is verified.")
        else:
            print("The hash does not match. The message is not verified.")
    else:
        print("Skipping verification.")

if __name__ == "__main__":
    main()
