# Terminal Snake Game

## Description
The singleplayer directory contains the code for a terminal snake game in under 50 lines of Python. It was written using the curses library. 

I made a video about it on my YouTube channel: https://www.youtube.com/watch?v=ado_xHizvMc

The multi-player directory contains the code for a multiplayer snake game using sockets. 

## Running the Code
### Singleplayer
If you are on Windows, you will need to install curses. This step is not needed for Linux or Mac users.
```
pip install windows-curses
```
Run the game.
```
cd singleplayer
python3 snake-game.py
```
### Multiplayer
Running the server:
```
cd multiplayer/server
python3 server.py
```
Running the client:
```
cd multiplayer/client
python3 client.py
```
Connect to the IP address of the machine running the server.