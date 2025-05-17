import queue
import socket
import threading
import time

from connection import Connection
from logging_utils import log_message
from state import State


class Server:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.state = State()
		self.connections = []
		self.message_queue = queue.Queue()

		self.state_lock = threading.Lock()
		self.conn_lock = threading.Lock()


	# Logs a message
	def log_message(self, type, message):
		log_message(type, "Server", message)


	# Starts the server
	def start(self):
		self.socket.bind((self.host, self.port))
		self.socket.listen()
		self.log_message("INFO", f"Server running on {self.host}:{self.port}")
		self.log_message("INFO", f"Local server IP: {socket.gethostbyname(socket.gethostname())}")

		# Main game loop updates
		threading.Thread(target=self.broadcast_loop, daemon=True).start()

		# Process messages from connections
		threading.Thread(target=self.process_messages, daemon=True).start()

		# Main listening loop
		try:
			while True:
				conn, address = self.socket.accept()
				new_conn = Connection(conn, address, self.message_queue)	
				self.log_message("INFO", f"New client connected: {new_conn.address}")

				threading.Thread(target=new_conn.handle, daemon=True).start()

		except KeyboardInterrupt:
			self.log_message("WARNING", f"Keyboard interrupt, quitting server")
		finally:
			self.close()


	# Closes down the server
	def close(self):
		self.log_message("INFO", f"Closing down server on {self.host}:{self.port}")

		with self.conn_lock:
			for connection in self.connections:
				connection.socket.close()

		self.socket.close()


	# Polls the queue and processes the messages
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

			elif 'remove_connection' in message:
				# Remove the player from game state and connection pool
				self.remove_player(message['remove_connection'])	


	# Sends a message to all connected clients
	def broadcast(self, message):
		with self.conn_lock:
			for connection in list(self.connections):
				connection.send(message)


	# Updates the game state and sends out the new state
	def broadcast_loop(self):
		while True:
			with self.state_lock:
				self.state.update_state()
				message = self.state.to_json()
			
			self.broadcast(message)
			time.sleep(0.075)


	# Adds a player to the game and add to connection pool
	def add_player(self, connection, username):
		with self.state_lock:
			unique_username = self.state.get_unique_username(username)
			self.state.add_player(unique_username)
			connection.username = unique_username

		# Send the unique username back to the client
		connection.send(unique_username)

		with self.conn_lock:
			self.connections.append(connection)
			self.log_message("DEBUG", f"List of connections: {[conn.address for conn in self.connections]}")


	# Removes a player from the game state and connections list
	def remove_player(self, connection):
		with self.state_lock:
			self.state.remove_player(connection.username)

		connection.socket.close()

		with self.conn_lock:
			if connection in self.connections:
				self.connections.remove(connection)			
				self.log_message("DEBUG", f"List of connections: {[conn.address for conn in self.connections]}")	


if __name__ == "__main__":
	host = "0.0.0.0"
	port = 5050

	server = Server(host, port)
	server.start()

	server.log_message("INFO", "Main function ended, cleaning up")
	server.close()
