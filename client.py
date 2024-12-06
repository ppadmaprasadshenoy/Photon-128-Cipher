import socket
import json
from photon128 import photon128  

class PhotonClient:
    def __init__(self, host='localhost', port=5000):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

    def send_message(self, message):
        """Send a message and its hash"""
        # Generate hash for the message
        hash_value = photon128(message.encode('utf-8'))
        
        # Create message package
        data = {
            'type': 'message',
            'message': message,
            'hash': hash_value.hex()
        }

        print("Generated hash:", data['hash'])
        
        # Send the message
        self.client.send(json.dumps(data).encode('utf-8'))

    def request_messages(self):
        data = {'type': 'request_messages'}
        self.client.send(json.dumps(data).encode('utf-8'))

    def verify_message(self, message, received_hash):
        calculated_hash = photon128(message.encode('utf-8'))
        return calculated_hash.hex() == received_hash

    def display_message_history(self, messages):
        print("\n" + "="*50)
        print(" "*15 + "MESSAGE HISTORY")
        print("="*50 + "\n")
        
        if not messages:
            print("No messages in history.")
            return
            
        for i, msg in enumerate(messages, 1):
            print(f"Message #{i}")
            print("-" * 30)
            print(f"Content: {msg['message']}")
            print(f"Hash   : {msg['hash']}")
            verification = "✓ SUCCESS" if self.verify_message(msg['message'], msg['hash']) else "✗ FAILED"
            print(f"Verify : {verification}")
            print()  # Empty line between messages
        
        print("="*50 + "\n")

    def display_single_message(self, data):
        print("\n" + "-"*50)
        print("NEW MESSAGE RECEIVED")
        print("-"*50)
        print(f"Content: {data['message']}")
        print(f"Hash   : {data['hash']}")
        verification = "✓ SUCCESS" if self.verify_message(data['message'], data['hash']) else "✗ FAILED"
        print(f"Verify : {verification}")
        print("-"*50 + "\n")

    def receive_messages(self):
        """Receive and process messages"""
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if not message:
                    break
                
                data = json.loads(message)
                
                if data['type'] == 'message':
                    self.display_single_message(data)
                
                elif data['type'] == 'message_history':
                    self.display_message_history(data['messages'])
                
            except Exception as e:
                print(f"Error: {e}")
                break

    def display_menu(self):
        """Display the menu options"""
        print("\nOptions:")
        print("╔════════════════════════════╗")
        print("║ 1. Send a message          ║")
        print("║ 2. Request message history ║")
        print("║ 3. Exit                    ║")
        print("╚════════════════════════════╝")

    def start(self):
        """Start the client interface"""
        # Start receiving messages in a separate thread
        from threading import Thread
        receive_thread = Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        while True:
            self.display_menu()
            choice = input("Choose an option (1-3): ")
            
            if choice == '1':
                message = input("Enter your message: ")
                self.send_message(message)
            elif choice == '2':
                self.request_messages()
            elif choice == '3':
                break
            else:
                print("Invalid option")

if __name__ == "__main__":
    client = PhotonClient()
    client.start()

        
        
       