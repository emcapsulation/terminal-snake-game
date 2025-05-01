import json
import random

from logging_utils import get_logger, log_message
from player import Player

class State:
	DIRECTION_MAP = {
		ord("w"): [-1, 0],
		ord("a"): [0, -1],
		ord("s"): [1, 0],
		ord("d"): [0, 1]
	}


	def __init__(self, dimensions):
		self.dimensions = dimensions
		self.food_pos = self.get_random_position()
		self.players = {}
		self.logger = get_logger(__name__)


	# Logs a message
	def log_message(self, type, message):
		log_message(self.logger, type, f"State", message)


	# Converts the object to JSON so it can be sent to the client
	def to_json(self):
		return json.dumps({
			"dimensions": self.dimensions,
			"food_pos": self.food_pos,
			"players": {username: player.to_dict() for username, player in self.players.items()}
		})


	# Adds a new player to the map
	def add_player(self, username):	
		start_segment = [self.get_random_position()]
		random_direction = State.DIRECTION_MAP[ord(random.choice(["w", "a", "s", "d"]))]
		player = Player(start_segment, random_direction)

		self.players[username] = player	
		self.log_message("INFO", f"Player {username}: Added to list of players")	


	# Gets a random position
	def get_random_position(self):
		return [random.randint(1, self.dimensions[0]-2), random.randint(1, self.dimensions[1]-2)]


	# Removes a player from the map
	def remove_player(self, username):
		self.log_message("INFO", f"Player {username}: Removing from list of players")
		self.players.pop(username)


	# Where everything gets updated
	def update_state(self):
		self.update_snakes()
		# self.sort_leaderboard()


	# Gets the segments from all snakes
	def get_occupied_positions(self):
		occupied_positions = []

		for player in self.players.values():
			occupied_positions.extend(player.segments)

		return occupied_positions


	# Regenerates the food if a snake ate it
	def regenerate_food(self, eater, occupied_positions):
		if eater is not None:
			self.log_message("INFO", f"Player {eater}: Ate food")

			self.food_pos = self.get_random_position()
			while self.food_pos in occupied_positions:
				self.food_pos = self.get_random_position()
			
			self.players[eater].score += 1


	# Moves all snakes one step
	def update_snakes(self):
		occupied_positions = self.get_occupied_positions()
		eater = None
		for username, player in self.players.items():
			# Add the new head
			player.add_new_head()
			
			# Update whether he survived the move
			player.update_is_alive(occupied_positions, self.dimensions)
			if not player.is_alive:
				self.log_message("INFO", f"Player {username}: Has died")
				continue

			# Check if he ate food
			if player.get_head() != self.food_pos: 
				player.pop_tail()
			else:
				eater = username

		# Snake got the food		
		self.regenerate_food(eater, occupied_positions)


	# Updates the player's direction
	def update_player_direction(self, username, key):
		if username in self.players:
			player = self.players[username]			

			new_dir = State.DIRECTION_MAP[ord(key)]
			if [new_dir[0]+player.direction[0], new_dir[1]+player.direction[1]] != [0, 0]:
				player.direction = new_dir
				self.log_message("INFO", f"Player {username}: Direction updated to {key}")

			
