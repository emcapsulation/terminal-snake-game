import json
import socket
import threading

from render import Render


class Client:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.username = ""
		self.render = None


	# Starts the client
	def start(self):
		try:
			self.socket.connect((self.host, self.port))
		except Exception as e:
			self.close(f"ERROR - Could not connect to server: {self.host}:{self.port}")
		else:
			print(f"Connected to server on {self.host}:{self.port}")
			self.send_username()
			self.receive_unique_username()
			self.update_render()


	# Closes connection and cleans up render
	def close(self, message):
		if self.render is not None:
			self.render.cleanup()
		self.socket.close()
		print(message)


	# Sends a message
	def send(self, message):
		try:
			self.socket.sendall(message.encode() + b'\n')
		except Exception as e:
			self.close("Could not send message to the server.")


	# Sends a username upon first join
	def send_username(self):
		username = input("Enter your username: ").strip()
		self.send(json.dumps({'username': username}))


	# Receives the unique username back from the server
	def receive_unique_username(self):
		username = self.socket.recv(1024).decode().strip()
		if not username:
			self.close("Could not receive initial game state.")
		else:
			self.username = username
			print(f"Welcome, {self.username}")


	# Draw the initial game window
	def init_render(self, dimensions):
		self.render = Render(self.username, dimensions, self)
		threading.Thread(target=self.render.capture_keypress, daemon=True).start()


	# Redraws the game window based on the new state
	def update_render(self):
		try:
			buffer = ""
			running = True

			while running:
				data = self.socket.recv(4096).decode()
				if not data:
					break

				buffer += data

				while "\n" in buffer:
					line, buffer = buffer.split("\n", 1)
					state = json.loads(line)

					# Initial paint
					if self.render == None:
						self.init_render(state['dimensions'])

					# Player has been removed from the game
					if self.username not in state['players']:
						running = False
						break

					self.render.update_state(state)

		except KeyboardInterrupt:
			print("Keyboard interrupt - quitting game.")
		except Exception as e:
			pass
		finally:
			self.close("Game over.")


if __name__ == "__main__":
	server_ip = input("Enter the server IP address: ")
	port = 5050

	client = Client(server_ip, port)
	client.start()
	client.close("Ending game.")