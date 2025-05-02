# Singleplayer Terminal Snake Game

## Description
The single-player directory contains the code for a terminal snake game in under 50 lines of Python. It was written using the curses library. 

I made a video about it on my YouTube channel: https://www.youtube.com/watch?v=ado_xHizvMc

## Running the Code
If you are on Windows, you will need to install curses. This step is not needed for Linux or Mac users.
```
pip install windows-curses
```
Run the game.
```
cd single-player
python3 snake-game.py
```

# Multiplayer Terminal Snake Game

## Description
The multi-player directory contains the code for a multiplayer snake game using sockets. 

## Running the Code
Running the server:
```
cd multi-player/server
python3 server.py
```
Running the client:
```
cd multi-player/client
python3 client.py
```