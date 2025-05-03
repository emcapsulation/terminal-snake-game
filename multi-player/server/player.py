import json

class Player:
	def __init__(self, segments, direction):
		self.segments = segments
		self.direction = direction
		self.score = 0
		self.is_alive = True


	# Converts the object to JSON so it can be sent to the client
	def to_dict(self):
		return {
			"segments": self.segments,
			"direction": self.direction,
			"score": self.score,
			"is_alive": self.is_alive
		}


	# Returns the head of the snake
	def get_head(self, j=None):
		if len(self.segments) > 0:
			if j != None:
				return self.segments[0][j]
			return self.segments[0]
		else:
			return None


	# Adds the new head in the current direction
	def add_new_head(self):
		new_head = [self.get_head(0)+self.direction[0], self.get_head(1)+self.direction[1]]
		self.segments.insert(0, new_head)


	# Pops the tail (used for movement)
	def pop_tail(self):
		self.segments.pop()


	# Kills the snake and performs cleanup
	def kill_snake(self):
		self.is_alive = False
		self.segments = []


	# Updates whether the snake is alive by checking for collision with a wall or another snake
	def update_is_alive(self, occupied_positions, dimensions):
		if self.get_head() == None:
			self.kill_snake()

		# Collide with another snake
		if self.get_head() in occupied_positions:
			self.kill_snake()

		# Collide with wall
		if self.get_head(0) in [0, dimensions[0]-1] or self.get_head(1) in [0, dimensions[1]-1]:
			self.kill_snake()

