from logging_utils import log_message

class Player:
	def __init__(self, segments, direction, colour_pair_id):
		self.segments = segments
		self.direction = direction
		self.score = 0
		self.colour = colour_pair_id


	# Logs a message
	def log_message(self, type, message):
		log_message(type, "Player", f"{message}")


	# Converts the object to a dictionary
	def to_dict(self):
		return {
			"segments": self.segments,
			"direction": self.direction,
			"score": self.score,
			"colour": self.colour
		}


	# Returns the head of the snake
	def get_head(self, j=None):
		if j is not None:
			return self.segments[0][j]
		return self.segments[0]


	# Adds the new head in the current direction
	def add_new_head(self):
		new_head = [self.get_head(0)+self.direction[0], 
			self.get_head(1)+self.direction[1]]
		self.segments.insert(0, new_head)


	# Pops the tail (for movement)
	def pop_tail(self):
		self.segments.pop()


	# Updates whether the snake is alive by checking for a collision
	def check_is_alive(self, occupied_positions, dimensions):
		if self.get_head(0) in [0, dimensions[0]-1] or self.get_head(1) in [0, dimensions[1]-1]:
			self.log_message("DEBUG", "Player hit wall")
			return False

		elif self.get_head() in occupied_positions:
			self.log_message("DEBUG", "Player collided with a segment")
			return False		

		return True

