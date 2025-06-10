# Terminal Snake Game

## Description
The singleplayer directory contains the code for a terminal snake game in under 50 lines of Python. It was written using the curses library. 

The multiplayer directory contains the code for a multiplayer snake game using sockets and threads. 

I made videos about these on my YouTube channel.
Singleplayer: https://www.youtube.com/watch?v=ado_xHizvMc
Multiplayer: https://www.youtube.com/watch?v=HkpvvkFWBwM

## Running the Code
If you are on Windows, you will need to install curses. This step is not needed for Linux or Mac users.
```
pip install windows-curses
```
### Singleplayer
```
cd singleplayer
python3 snake-game.py
```
### Multiplayer
In one terminal or command prompt, run the server:
```
cd multiplayer/server
python3 server.py
```
It will display your machine's local IP address.

Anyone who wants to play the game should run the client:
```
cd multiplayer/client
python3 client.py
```
Tell them to connect to the IP address of the machine running the server. You can play it by yourself if you want - just run the client in a separate terminal / command prompt.