import socket
import threading
import json
import time
from game_state import GameState

class Server:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.state = GameState([20, 50])
		self.connections = {}

		self.lock = threading.Lock()


	# Logs a message
	def log_message(self, type, message):
		print(f"{type.ljust(7, ' ')} | {message}")


	# Starts the server
	def start(self):
		self.server.bind((self.host, self.port))
		self.server.listen()
		self.log_message("INFO", f"Server running on {self.host}:{self.port}")

		# Main game loop updates
		threading.Thread(target=self.broadcast_loop, daemon=True).start()

		while True:
			client_socket, client_address = self.server.accept()
			self.log_message("INFO", f"New client connected: {client_address}")						

			client_thread = threading.Thread(target=self.handle, args=(client_socket, client_address), daemon=True)
			client_thread.start()


	# Receives a new client's username
	def receive_username(self, client_socket, client_address):
		try:
			username = client_socket.recv(1024).decode().strip()	
			self.log_message("INFO", f"Received username from {client_address}: {username}")
			self.add_player(client_socket, client_address, username)
			return username
		except Exception as e:
			self.log_message("ERROR", f"receive_username: {e}")
			self.remove_player(username)	


	# Handles an incoming client
	def handle(self, client_socket, client_address):
		username = self.receive_username(client_socket, client_address)

		try:
			while True:			
				data = client_socket.recv(1024)	
				if not data:
					break
		except Exception as e:
			self.log_message("ERROR", f"handle: {e}")
		finally:
			self.remove_player(username)


	# Sends a message to all clients
	def broadcast(self, message):
		message_bytes = json.dumps(message).encode() + b"\n"
		for user in self.connections:
			client_socket = self.connections[user]['client_socket']
			try:
				client_socket.sendall(message_bytes)
				self.log_message("INFO", f"Message broadcasted: {message}")
			except Exception as e:
				self.log_message("ERROR", f"broadcast: {e}")
				self.remove_player(user)			


	# The main game update loop
	def broadcast_loop(self):
		while True:
			dead_snakes = []

			with self.lock:
				dead_snakes = self.state.update_state()
				self.broadcast(self.state.game_state)

			for user in dead_snakes:
				self.remove_player(user)

			time.sleep(0.075)


	# Adds a player to the game by username
	def add_player(self, client_socket, client_address, username):
		with self.lock:
			self.connections[username] = {'client_socket': client_socket, 'client_address': client_address}
			self.state.add_player(username)

			self.log_message("INFO", f"Player added {client_address}: {username}")
			self.log_message("INFO", f"Connections: {self.connections}")


	# Removes a player from the game state and connections list
	def remove_player(self, user):
		with self.lock:
			self.state.remove_player(user)
			self.log_message("INFO", f"Player removed: {user}")

			self.connections[user]['client_socket'].close()
			self.log_message("INFO", f"Connection closed: {user}")

			self.connections.pop(user)			
			self.log_message("INFO", f"Players: {self.connections}")			
	

if __name__ == "__main__":
	host = socket.gethostbyname(socket.gethostname())
	port = 5050

	server = Server(host, port)
	server.start()
