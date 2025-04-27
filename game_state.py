import random

class GameState:
	def __init__(self, dimensions):
		self.dimensions = dimensions

		self.game_state = {
			'dimensions': self.dimensions,
			'food_pos': [random.randint(1, self.dimensions[0]-2), random.randint(1, self.dimensions[1]-2)],
			'players': {}
		}

		self.dirs = {
			ord("w"): [-1, 0],
			ord("a"): [0, -1],
			ord("s"): [1, 0],
			ord("d"): [0, 1]
		}


	# Adds a new player to the map
	def add_player(self, username):
		player = {
			'segments': [[random.randint(1, self.dimensions[0]-2), random.randint(1, self.dimensions[1]-2)]],
			'score': 0,
			'direction': self.dirs[ord(random.choice(["w", "a", "s", "d"]))]
		}

		self.game_state['players'][username] = player


	# Removes a player from the map
	def remove_player(self, username):
		self.game_state['players'].pop(username)


	# Where everything gets updated
	def update_state(self):
		dead_snakes = self.move_snakes()
		# self.sort_leaderboard()

		return dead_snakes


	# Gets the segments from all snakes
	def get_all_segments(self):
		all_segments = []

		for user, snake in self.game_state['players'].items():
			all_segments.extend(snake)

		return all_segments


	# Checks if the snake has died
	def snake_alive(self, all_segments, head):
		if head in all_segments or head[0] in [0, self.dimensions[0]-1] or head[1] in [0, self.dimensions[1]-1]:
			return False
		return True


	# Regenerates the food if a snake ate it
	def regenerate_food(self, food_eaten_by, all_segments):
		if food_eaten_by != None:
			self.game_state['food_pos'] = [random.randint(1, self.dimensions[0]-2), random.randint(1, self.dimensions[1]-2)]
			while self.game_state['food_pos'] in all_segments:
				self.game_state['food_pos'] = [random.randint(1, self.dimensions[0]-2), random.randint(1, self.dimensions[1]-2)]
			
			self.game_state['players'][food_eaten_by]['score'] += 1


	# Moves all snakes one step
	def move_snakes(self):
		dead_snakes = []
		all_segments = self.get_all_segments()

		food_eaten_by = None
		for user, snake in self.game_state['players'].items():
			# Add the new head
			head = [snake['segments'][0][0]+snake['direction'][0], snake['segments'][0][1]+snake['direction'][1]]
			
			# Check if he survived the move
			alive = self.snake_alive(all_segments, head)
			if not alive:
				dead_snakes.append(user)
				continue

			snake['segments'].insert(0, head)

			# Check if he ate food
			if head != self.game_state['food_pos']: 
				snake['segments'].pop()
			else: 
				food_eaten_by = user

		# Snake got the food		
		self.regenerate_food(food_eaten_by, all_segments)

		# Return the list of dead snakes
		return dead_snakes


	# # Sorts all the snakes based on scores
	# def 
