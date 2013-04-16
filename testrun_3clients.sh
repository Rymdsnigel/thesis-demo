#!/usr/bin/env bash

python server.py & python client.py --port=10001 --framerate=1000 --x=300 --y=300 & python client.py --port=10002 --framerate=1000 --x=300 --y=300 & python client.py --port=10003 --framerate=1000 --x=200 --y=200

