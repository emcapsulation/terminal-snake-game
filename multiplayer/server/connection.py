import json
import traceback

from logging_utils import log_message

class Connection:
	def __init__(self, socket, address, message_queue):
		self.socket = socket
		self.address = address
		self.message_queue = message_queue
		self.username = None


	# Logs a message
	def log_message(self, type, message):
		log_message(type, str(self.username), f"{self.address}: {message}")


	# Closes this connection
	def close(self):
		self.socket.close()
		self.log_message("WARNING", f"Connection closed")
		self.add_to_queue({"remove_connection": self})


	# Sends a message
	def send(self, message):
		try:
			self.socket.sendall(message.encode() + b'\n')
		except Exception as e:
			self.log_message("ERROR", traceback.format_exc())


	# Adds a message to the queue
	def add_to_queue(self, message):
		self.message_queue.put((self, message))	
		self.log_message("INFO", f"Message added to queue: {message}")		


	# Basic handler - listens for messages
	def handle(self):
		try:
			# Get the initial username for the new connection	
			self.receive_username()

			buffer = ""
			while True:
				data = self.socket.recv(1024).decode()
				if not data:
					break

				buffer += data

				# Process the received data and add to queue
				while "\n" in buffer:
					message, buffer = buffer.split("\n", 1)
					msg = self.parse_message(message)

					if msg is not None:
						self.add_to_queue(msg)

		except Exception as e:
			self.log_message("ERROR", traceback.format_exc())
		finally:
			self.close()


	# Parses a message - it should be in JSON format
	def parse_message(self, msg):
		parsed_msg = None
		try:
			parsed_msg = json.loads(msg)
		except Exception as e:
			self.log_message("ERROR", traceback.format_exc())	
		finally:
			return parsed_msg


	# Receives the username from the client
	def receive_username(self):
		username = self.socket.recv(1024).decode().strip()
		if not username:
			raise Exception("Username not received.")
		else:
			self.log_message("INFO", f"Received username: {username}")
			username_json = self.parse_message(username)
			self.add_to_queue(username_json)


	# Sends the unique username back to the client
	def send_username(self, username):
		try:
			self.log_message("INFO", f"Sending unique username: {username}")
			self.send(username)
		except Exception as e:
			self.close()		