import curses
import json

class GameRender:
	def __init__(self, username, dimensions, client_socket):
		self.username = username
		self.dimensions = dimensions
		self.client_socket = client_socket

		self.stdscr = curses.initscr()
		self.game_state = None

		self.create_game_window()


	# Creates the game window
	def create_game_window(self):			
		curses.curs_set(0)	
		curses.noecho()
		self.stdscr.clear()
		self.stdscr.timeout(75)

		self.height, self.width = self.dimensions
		self.win = curses.newwin(self.height, self.width, 0, 0)
		self.win.clear()
		self.win.border()	


	# Cleans everything
	def cleanup(self):
		curses.echo()
		curses.endwin()


	# Updates the game state
	def update_game_state(self, new_state):
		try:
			if self.game_state == None:
				self.game_state = new_state
				self.initial_draw()	
			else:
				self.redraw(new_state)

		except Exception:
			self.cleanup()


	# Draws an entire snake to the screen
	def draw_snake(self, segments):
		for segment in segments:
			self.win.addch(*segment, curses.ACS_BOARD)


	# Draws the current user's score to the screen
	def draw_score(self, score):
		self.win.addstr(self.height-1, self.width-12, f"Score: {score}")


	# Draws the food to the screen
	def draw_food(self, food_pos):
		self.win.addch(*food_pos, '@')


	# Draws everything for the first time
	def initial_draw(self):
		self.draw_food(self.game_state['food_pos'])

		for username, snake in self.game_state['players'].items():
			self.draw_snake(snake['segments'])

		self.draw_score(self.game_state['players'][self.username]['score'])
		self.win.refresh()
	

	# Includes optimisations rather than redrawing everything
	def redraw(self, new_state):
		# Redraw food
		if new_state['food_pos'] != self.game_state['food_pos']:
			self.draw_food(new_state['food_pos'])
			self.win.addch(*self.game_state['food_pos'], ' ')

		# Update snakes
		for user, new_snake in new_state['players'].items():
			if user in self.game_state['players']:
				current_snake = self.game_state['players'][user]

				# Add head(s)
				i = 0
				while i < len(new_snake['segments']) and new_snake['segments'][i] not in current_snake['segments']:
					self.win.addch(*new_snake['segments'][i], curses.ACS_BOARD)
					i += 1		

				# Pop tail(s)
				i = len(current_snake['segments'])-1
				while i >= 0 and current_snake['segments'][i] not in new_snake['segments']:				
					self.win.addch(*current_snake['segments'][i], ' ')
					i -= 1

			else:
				# New user, draw whole snake
				self.draw_snake(new_snake['segments'])

		# Update score
		new_score = new_state['players'][self.username]['score']
		cur_score = self.game_state['players'][self.username]['score']
		if new_score != cur_score:
			self.draw_score(new_score)

		self.win.refresh()
		self.game_state = new_state


	def capture_keypress(self):
	    try:
	        while True:
	            key = self.stdscr.getch()

	            if key == ord("w") or key == ord("a") or key == ord("s") or key == ord("d"):
	                message = json.dumps({'direction': chr(key)})
	                self.client_socket.sendall(message.encode())

	    except Exception as e:
	        print(f"ERROR in capture_keypress: {e}")
	        self.cleanup()