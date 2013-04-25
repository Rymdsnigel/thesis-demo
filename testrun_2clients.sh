#!/usr/bin/env bash

python server.py &
sleep 3
python client.py  --port=10001 --framerate=0 --x=300 --y=300 --pos=0.0,0.0,0.5,1.0 &
python client.py --port=10002 --framerate=0 --x=300 --y=300 --pos=0.5,0.0,1.0,1.0