import json
import socket
import queue
import threading
import time

from connection import Connection
from game_state import GameState
from logging_utils import get_logger, log_message


class Server:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.state = GameState([20, 50])
		self.connections = []
		self.message_queue = queue.Queue()

		self.lock = threading.Lock()
		self.logger = get_logger(__name__)


	def log_message(self, type, message):
		log_message(self.logger, type, "Server", message)


	# Starts the server
	def start(self):
		self.server.bind((self.host, self.port))
		self.server.listen()
		self.log_message("INFO", f"Server running on {self.host}:{self.port}")

		# Main game loop updates
		threading.Thread(target=self.broadcast_loop, daemon=True).start()

		# Process messages from connections
		threading.Thread(target=self.process_messages, daemon=True).start()

		while True:
			client_socket, client_address = self.server.accept()
			new_conn = Connection(client_socket, client_address, self.message_queue)			
			self.log_message("INFO", f"New client connected: {new_conn.address}")			

			# Get the initial username for the new connection
			new_conn.receive_username()

			# Add to the pool of connections
			with self.lock:
				self.connections.append(new_conn)
				self.log_message("INFO", f"List of connections: {[conn.address for conn in self.connections]} ")

			# Add the player to the game state
			self.add_player_to_game(new_conn)

			client_thread = threading.Thread(target=new_conn.handle, daemon=True)
			client_thread.start()


	# Loops through queue and processes messages
	def process_messages(self):
		while True:
			connection, message = self.message_queue.get()

			self.log_message("INFO", f"Next message: {connection.username} - {message}")
			if 'direction' in message:
				self.state.update_player_direction(connection.username, message['direction'])
				self.log_message("INFO", f"Updated direction of {connection.username} to {message['direction']}")
			elif 'remove_connection' in message:
				self.remove_player(message['remove_connection'])	


	# Sends a message to all clients
	def broadcast(self, message):
		message_bytes = message.encode() + b"\n"

		for connection in self.connections:
			try:
				connection.socket.sendall(message_bytes)
			except Exception as e:
				self.log_message("ERROR", f"broadcast: {e}")
				self.remove_player(connection)


	# Updates everyone's states and sends out the new state
	def broadcast_loop(self):
		while True:
			with self.lock:
				self.state.update_state()
				self.broadcast(self.state.to_json())
			time.sleep(0.075)


	# Adds a player to the game by username
	def add_player_to_game(self, connection):
		with self.lock:
			self.state.add_player(connection.username)
			self.log_message("INFO", f"{connection.address} {connection.username}: Player added to game")			


	# Removes a player from the game state and connections list
	def remove_player(self, connection):
		with self.lock:
			self.state.remove_player(connection.username)
			self.log_message("INFO", f"{connection.address} {connection.username}: Player removed from game")

			self.connections.remove(connection)			
			self.log_message("INFO", f"List of connections: {[conn.address for conn in self.connections]} ")		


if __name__ == "__main__":
	host = socket.gethostbyname(socket.gethostname())
	port = 5050

	server = Server(host, port)
	server.start()
