import json
import socket
import queue
import threading
import time

from connection import Connection
from state import State
from logging_utils import get_logger, log_message


class Server:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.state = State()
		self.connections = []
		self.message_queue = queue.Queue()

		self.state_lock = threading.Lock()
		self.conn_lock = threading.Lock()

		self.logger = get_logger(__name__)


	def log_message(self, type, message):
		log_message(self.logger, type, "Server", message)


	# Shuts down the server
	def close(self):
		self.log_message("INFO", f"Shutting down server on {self.host}:{self.port}")

		with self.conn_lock:
			for connection in self.connections:
				connection.socket.close()

		self.server.shutdown(socket.SHUT_RDWR)
		self.server.close()


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

			client_thread = threading.Thread(target=new_conn.handle, daemon=True).start()


	# Loops through queue and processes messages
	def process_messages(self):
		while True:
			connection, message = self.message_queue.get()
			self.log_message("INFO", f"Next message: {connection.username} - {message}")

			if 'username' in message:
				# Add the player to the game state and connection pool
				self.add_player(connection, message['username'])

			elif 'direction' in message:
				# Update player direction
				with self.state_lock:
					self.state.update_player_direction(connection.username, message['direction'])
					self.log_message("INFO", f"Updated direction of {connection.username} to {message['direction']}")

			elif 'remove_connection' in message:
				# Remove client
				self.remove_player(message['remove_connection'])	


	# Sends a message to all clients
	def broadcast(self, message):
		message_bytes = message.encode() + b"\n"

		with self.conn_lock:
			for connection in list(self.connections):
				try:
					connection.socket.sendall(message_bytes)
				except Exception as e:
					self.log_message("ERROR", f"broadcast: {e}")
					self.remove_player(connection)


	# Updates everyone's states and sends out the new state
	def broadcast_loop(self):
		while True:
			with self.state_lock:
				self.state.update_state()
				message = self.state.to_json()
			
			self.broadcast(message)
			time.sleep(0.075)


	# Adds a player to the game by username, add to connection pool
	def add_player(self, connection, username):
		unique_username = username

		with self.state_lock:
			unique_username = self.state.get_unique_username(username)
			self.state.add_player(unique_username)
			connection.username = unique_username

		# Send the unique username back to the client
		connection.send_username(unique_username)

		with self.conn_lock:
			self.connections.append(connection)
			self.log_message("INFO", f"List of connections: {[conn.address for conn in self.connections]} ")


	# Removes a player from the game state and connections list
	def remove_player(self, connection):
		with self.state_lock:
			self.state.remove_player(connection.username)

		with self.conn_lock:
			if connection in self.connections:
				self.connections.remove(connection)			
				self.log_message("INFO", f"List of connections: {[conn.address for conn in self.connections]} ")	


if __name__ == "__main__":
	host = socket.gethostbyname(socket.gethostname())
	port = 5050

	server = Server(host, port)

	try:
		server.start()
	except Exception as e:
		server.log_message("CRITICAL", f"Fatal server error: {e}")
	finally:
		server.close()
