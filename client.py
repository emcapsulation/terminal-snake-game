import socket
import json
import threading
from game_render import GameRender

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.username = ""
        self.render = None


    # Logs a message
    def log_message(self, type, message):
        print(f"{type.ljust(7, ' ')} | {message}")


    # The main loop
    def main(self):
        self.connect()
        self.submit_username()
        self.update_render()


    # Connect to server
    def connect(self):               
        self.client.connect((self.host, self.port))
        self.log_message("INFO", f"Connected to server at {self.host}:{self.port}")


    # Closes connection and cleans up render
    def close(self):
        if self.render != None:
            self.render.cleanup()
        self.client.close()
        self.log_message("INFO", f"Connection closed")


    # Sends a username upon first join
    def submit_username(self):
        username = input("Enter your username: ").strip()
        self.username = username

        try:
            self.client.sendall(self.username.encode())
        except Exception as e:
            self.log_message("ERROR", f"submit_username: {e}")
            self.client.close()
            self.log_message("INFO", f"Connection closed")


    # Receives the initial game state
    def receive_initial_game_state(self):
        self.receive_dimensions()


    # Initial paint of the window
    def init_render(self, dimensions):
        self.render = GameRender(self.username, dimensions)
        self.render.main() 


    # Redraws the game window based on the new state
    def update_render(self):        
        try:
            buffer = ""
            while True:
                data = self.client.recv(4096).decode()
                if not data:
                    break

                buffer += data

                if "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    game_state = json.loads(line)

                    # Initial paint
                    if self.render == None:
                        self.init_render(game_state['dimensions'])

                    status_code = self.render.update_game_state(game_state)
                    if status_code == -1:
                        raise Exception("Render failed - probably went off screen")

        except Exception as e:
            self.log_message("ERROR", f"update_render: {e}")

        finally:
            self.close()         


if __name__ == "__main__":
    server_ip = socket.gethostbyname(socket.gethostname())
    port = 5050

    client = Client(server_ip, port)
    client.main()
