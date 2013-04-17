#-*- coding: utf-8 -*-
"""
Client rendering graphics

Usage:
  client.py [--port=<nr>]
            [--framerate=<frame/s>]
            [--x=<pixels>]
            [--y=<pixels>]
            [--pos <x1> <y1> <x2> <y2>]
  client.py (-h | --help)
  client.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --port=<nr>   Port number to bind to client [default: 5007].
  --framerate=<frame/s> Client framerate [default: 1000].
  --x=<pixels> Width of client screen [default: 300].
  --y=<pixels> Height of client screen [default: 300].
  --pos <x1> <y1> <x2> <y2> Position of the part of the animation the client shows.
"""

import pygame
import gevent
from gevent.queue import Queue
import math
import logging
from docopt import docopt
import tween
from implementations.ntpversion import NTPClient as Client


logger = logging.getLogger('test')
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler(filename='synclog.log')
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

HOST = 'localhost'
PORT = 5007

tasks = Queue()
id = ''

def to_local_pos(pos, client_pos):
    x_offset = client_pos[0]
    client_width = client_pos[2] - client_pos[0]
    client_height = client_pos[1] - client_pos[3]
    pos1 = (pos[0] - x_offset) / client_width
    pos2 = pos[1] / client_height
    return (pos1, pos2)

def to_pixel_pos(pos, client):
    return (pos[0]*client.width, pos[1]*client.height)

# Render
def render(client):
# Setup pygame
    screen = pygame.display.set_mode((client.width,client.height))
    pygame.display.set_caption("client rendering graphics")
    pygame.init()
    running = 1
    color = pygame.Color(100, 110, 50)
    pos = (0.48, 0.5)
    local_pos = to_local_pos(pos, client.pos)
    rect = pygame.Rect(to_pixel_pos(local_pos, client), (client.width/10, client.height/10))
    color_animation = tween.Tween()
    while running:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            running = 0
        if not tasks.empty():
            data = tasks.get()
            if data["data_id"] == 1: #do the coloranimation
                color_animation.play(50, 250, 200.0, True, timestamp=client.get_tick())
            if data["data_id"] == 2: #change position
                local_pos = to_local_pos(data["data_val"], client.pos)
                pixel_pos = to_pixel_pos(local_pos, client)
                #pos = (((data["data_val"][0])*client.width) - rect.left, 0)
                rect.left  = pixel_pos[0]
                #rect = rect.move(pos)
        if color_animation.running:
            color_animation.step(client.get_tick())
            if int(color_animation.value) <= 255:
                color.b = int(color_animation.value)
        val = ((1 + math.cos(client.get_tick()/250.0))/2)*client.height
        pos = (0, val - rect.top)
        rect = rect.move(pos)
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, color, rect)
        pygame.display.flip()
        pygame.time.Clock().tick(client.framerate)
        gevent.sleep(0)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Client 0.1')
    positions = [float(x) for x in arguments["--pos"].split(',')]
    client = Client(HOST, PORT, tasks, int(arguments["--framerate"]), positions, int(arguments["--x"]), int(arguments["--y"]), int(arguments["--port"]))
    client.start()
    gevent.joinall([
        client,
        gevent.spawn(render, client)
    ])

    pygame.quit()
