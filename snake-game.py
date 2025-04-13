import curses
import random

def main(stdscr):
	curses.curs_set(0)
	height, width = stdscr.getmaxyx()
	stdscr.border()
	stdscr.timeout(75)

	segments = [[1, 1]]
	stdscr.addch(*segments[0], curses.ACS_BOARD)
	food_pos = [random.randint(1, height-2), random.randint(1, width-2)]
	stdscr.addch(*food_pos, '@')	
	score = 0 
	stdscr.addstr(height-1, width-11, f"Score: {score}")

	dirs = {
		ord("w"): [-1, 0],
		ord("a"): [0, -1],
		ord("s"): [1, 0],
		ord("d"): [0, 1]
	}
	direction = [0, 1]
	
	while True:		
		key = stdscr.getch()
		if key in dirs and [dirs[key][0]+direction[0], dirs[key][1]+direction[1]] != [0, 0]:
			direction = dirs[key]

		head = [segments[0][0]+direction[0], segments[0][1]+direction[1]]
		if head[0] in [0, height-1] or head[1] in [0, width-1] or head in segments: 
			break

		segments.insert(0, head)
		stdscr.addch(*segments[0], curses.ACS_BOARD)

		if head != food_pos: 
			tail = segments.pop()
			stdscr.addch(*tail, ' ')

		else: 
			food_pos = [random.randint(1, height-2), random.randint(1, width-2)]
			while food_pos in segments:
				food_pos = [random.randint(1, height-2), random.randint(1, width-2)]
			stdscr.addch(*food_pos, '@')
			score += 1
			stdscr.addstr(height-1, width-11, f"Score: {score}")

curses.wrapper(main)