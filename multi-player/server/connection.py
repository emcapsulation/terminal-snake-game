import json

from logging_utils import get_logger, log_message

class Connection:
	def __init__(self, socket, address, message_queue):
		self.socket = socket
		self.address = address
		self.message_queue = message_queue
		self.username = None
		self.logger = get_logger(__name__)


	# Logs a message
	def log_message(self, type, message):
		log_message(self.logger, type, str(self.username), f"{self.address}: {message}")


	# Closes this connection
	def close(self):
		self.socket.close()
		self.log_message("INFO", f"Connection closed")
		self.add_to_queue({"remove_connection": self})


	# Adds a message to the queue
	def add_to_queue(self, message):
		self.message_queue.put((self, message))	
		self.log_message("INFO", f"Message added to queue: {message}")		


	# Basic handler - listens for messages
	def handle(self):
		try:
			# Get the initial username for the new connection	
			self.receive_username()

			while True:
				data = self.socket.recv(1024)
				if not data:
					break

				# Process the received data and add to queue
				messages = data.decode().split("\n")
				for message in messages:
					msg = self.parse_message(message)
					if msg != None:
						self.add_to_queue(msg)

		except Exception as e:
			self.log_message("ERROR", f"handle: {e}")

		finally:
			self.close()


	# Parses a message - it should be in JSON format
	def parse_message(self, msg):
		parsed_msg = None
		try:
			parsed_msg = json.loads(msg)
		except Exception as e:
			self.log_message("ERROR", f"Error parsing message '{msg}': {e}")	
		finally:
			return parsed_msg


	# Receives the username
	def receive_username(self):
		username = self.socket.recv(1024).decode().strip()
		if not username:
			raise Exception("Username not received.")
		else:
			self.log_message("INFO", f"Received username {username}")
			username_json = self.parse_message(username)
			self.username = username_json['username']
			self.add_to_queue({'username': self.username})

			



		