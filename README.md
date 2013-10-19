Synchronize rendering over a network. 
=============

This program explore the possibility to synchronize rendered animations in Realtime.  

It consists of a server and a client connected to each other via TCP-sockets. The clients each render a part of an animation and
are synchronized with each other communication with the server. 

Running the server
-------------
The server takes no parametes on start but it doesn't autoconnect to the clients so it has to be started before the clients.

    python server.py

Running the clients
-------------
An arbitrary number of clients can be started. Port, framerate, x, y, and pos needs to be passed as flags on startup.

    python client.py --port=10001 --framerate=0 --x=300 --y=300 --pos=0.0,0.0,0.5,1.0

Each client will render a part of the animation.

Running the server and two clients using script
------------

There is a included BASH-script to run a server and 2 clients
    ./testrun_2clients.sh 

Depencencies
-----------
Python
Gevent
pygame
