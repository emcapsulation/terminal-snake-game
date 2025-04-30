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
		log_message(self.logger, type, self.username, f"{self.address} message")


	# Basic handler - listens for messages
	def handle(self):
		try:
			while True:
				data = self.socket.recv(1024)
				if not data:
					break

				# Process the received data and add to queue
				messages = data.decode().split("\n")
				for message in messages:
					msg = self.parse_message(message)
					if msg != None:
						self.message_queue.put((self, msg))	
						self.log_message("INFO", f"Message added to queue: {msg}")			

		except Exception as e:
			self.log_message("ERROR", f"handle: {e}")

		finally:
			self.socket.close()
			self.log_message("INFO", f"Connection closed")
			self.message_queue.put((self, {"remove_connection": self}))


	# Parses a message - it should be in JSON format
	def parse_message(self, msg):
		parsed_msg = None
		try:
			parsed_msg = json.loads(msg)
		except Exception as e:
			self.log_message("ERROR", f"Error parsing message: {e}")	
		finally:
			return parsed_msg


	# Receives the username
	def receive_username(self):
		try:
			self.username = self.socket.recv(1024).decode().strip()
			self.log_message("INFO", f"Received username")
		except Exception as e:
			self.log_message("ERROR", f"receive_username: {e}")	

		