import curses
import json

class Render:
	LEADERBOARD_WIDTH = 15

	COLOUR_MAPPINGS = [
		[1, curses.COLOR_RED, curses.COLOR_BLACK],
		[2, curses.COLOR_GREEN, curses.COLOR_BLACK],
		[3, curses.COLOR_YELLOW, curses.COLOR_BLACK],
		[4, curses.COLOR_BLUE, curses.COLOR_BLACK],
		[5, curses.COLOR_MAGENTA, curses.COLOR_BLACK],
		[6, curses.COLOR_CYAN, curses.COLOR_BLACK],
		[7, curses.COLOR_WHITE, curses.COLOR_BLACK]
	]

	def __init__(self, username, dimensions, client):
		self.username = username
		self.dimensions = dimensions
		self.client = client

		self.stdscr = curses.initscr()
		self.state = None

		self.create_game_window()


	# Creates the game window
	def create_game_window(self):
		curses.curs_set(0)
		curses.noecho()

		self.stdscr.refresh()
		self.stdscr.timeout(75)

		curses.start_color()
		for mapping in Render.COLOUR_MAPPINGS:
			curses.init_pair(*mapping)

		self.height, self.width = self.dimensions
		self.win = curses.newwin(self.height, self.width, 0, 0)
		self.win.border()
		self.win.refresh()

		self.leaderboard_win = curses.newwin(self.height, Render.LEADERBOARD_WIDTH, 0, self.width+1)
		self.leaderboard_win.border()
		self.leaderboard_win.addstr(1, 1, "LEADERBOARD")		
		self.leaderboard_win.refresh()


	# Restores the terminal
	def cleanup(self):
		curses.endwin()


	# Updates the game state
	def update_state(self, new_state):
		try:
			self.draw(new_state)
			self.state = new_state
		except Exception:
			self.cleanup()


	# Includes optimisations rather than redrawing everything
	def draw(self, new_state):
		self.draw_food(new_state['food_pos'])
		self.draw_snakes(new_state['players'])
		self.draw_score(new_state['players'][self.username]['score'])
		self.draw_leaderboard(new_state['players'])

		self.win.refresh()
		self.leaderboard_win.refresh()


	def capture_keypress(self):
		try:
			while True:
				key = self.stdscr.getch()

				if key in [ord('w'), ord('a'), ord('s'), ord('d')]:
					message = json.dumps({'direction': chr(key)})
					self.client.send(message)

		except Exception as e:
			pass
		finally:
			self.cleanup()


	# Draws the leaderboard
	def draw_leaderboard(self, new_players):
		current_players = {} if self.state == None else self.state['players']

		# Remove dead players
		to_remove = len(current_players) - len(new_players)
		while to_remove > 0:
			self.leaderboard_win.addstr(len(current_players)+2-to_remove, 1, 
				self.format_leaderboard_string("", ""))
			to_remove -= 1

		# Add updated scores
		i = 2
		for username, snake in new_players.items():
			self.leaderboard_win.addstr(i, 1, 
				self.format_leaderboard_string(username, str(snake['score'])), 
				curses.color_pair(snake['colour']))
			i += 1


	# Formats the string for the leaderboard
	def format_leaderboard_string(self, username, score):
		total_length = Render.LEADERBOARD_WIDTH-2
		username_length = total_length-len(score)-1

		if len(username) > username_length:
			truncated_username = username[:username_length-3] + "..."
		else:
			truncated_username = username

		num_spaces = total_length-len(truncated_username)-len(score)
		return truncated_username + ' '*num_spaces + score


	# Draws the food to the screen
	def draw_food(self, new_food_pos):
		self.win.addch(*new_food_pos, '@')


	# Draws all snakes in the new state
	def draw_snakes(self, new_snakes):
		for username, new_snake in new_snakes.items():
			current_snake = []
			if self.state is not None and username in self.state['players']:
				current_snake = self.state['players'][username]['segments']
			self.update_snake(current_snake, new_snake['segments'], new_snake['colour'])

		# Remove eliminated snakes
		if self.state is not None:
			for username, current_snake in self.state['players'].items():
				if username not in new_snakes:
					self.update_snake(current_snake['segments'], [], current_snake['colour'])


	# Draws only the parts of the snakes which are different
	def update_snake(self, current_snake, new_snake, snake_colour):
		# Add head(s)
		i = 0
		while i < len(new_snake) and new_snake[i] not in current_snake:
			self.win.addch(*new_snake[i], curses.ACS_BOARD, curses.color_pair(snake_colour))
			i += 1

		# Pop tail(s)
		i = len(current_snake)-1
		while i >= 0 and current_snake[i] not in new_snake:				
			self.win.addch(*current_snake[i], ' ')
			i -= 1


	# Draws the current user's score to the screen
	def draw_score(self, new_score):
		if self.state == None or new_score != self.state['players'][self.username]['score']:
			self.win.addstr(self.height-1, self.width-12, f"Score: {new_score}")