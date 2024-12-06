import socket
import json
from threading import Thread
from photon128 import photon128  

class PhotonServer:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(2)  
        self.clients = []
        self.messages = []  

    def broadcast(self, message, sender=None):
        for client in self.clients:
            if client != sender:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    self.remove_client(client)

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if not message:
                    break
                
                data = json.loads(message)
                
                if data['type'] == 'message':
                    self.messages.append(data)
                    self.broadcast(message, client)
                elif data['type'] == 'request_messages':
                    response = json.dumps({'type': 'message_history', 'messages': self.messages})
                    client.send(response.encode('utf-8'))
                    
            except:
                break
        
        self.remove_client(client)

    def remove_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
            client.close()

    def start(self):
        print(f"Server is running on {self.host}:{self.port}")
        while True:
            client, address = self.server.accept()
            print(f"Connected with {address}")
            self.clients.append(client)
            
            # Start a new thread to handle the client
            thread = Thread(target=self.handle_client, args=(client,))
            thread.start()

if __name__ == "__main__":
    server = PhotonServer()
    server.start()