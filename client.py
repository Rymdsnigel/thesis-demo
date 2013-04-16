#-*- coding: utf-8 -*-
"""
Client rendering graphics

Usage:
  client.py [--port=<nr>]
            [--framerate=<frame/s>]
            [--x=<pixels>]
            [--y=<pixels>]
  client.py (-h | --help)
  client.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --port=<nr>   Port number to bind to client [default: 5007].
  --framerate=<frame/s> Client framerate [default: 1000].
  --x=<pixels> Width of client screen [default: 300].
  --y=<pixels> Height of client screen [default: 300].

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

# Setup pygame
screen = pygame.display.set_mode((300,300))
pygame.display.set_caption("client rendering graphics")
pygame.init()

# Render
def render(client):
    running = 1
    color = pygame.Color(100, 110, 50)
    rect = pygame.Rect(125, 125, 50, 50)
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
                pos = (((data["data_val"][0])*300) - rect.left, 0)
                rect = rect.move(pos)
        if color_animation.running:
            color_animation.step(client.get_tick())
            if int(color_animation.value) <= 255:
                color.b = int(color_animation.value)
        val = ((1 + math.cos(client.get_tick()/250.0))/2)*250
        pos = (0, val - rect.top)
        rect = rect.move(pos)
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, color, rect)
        pygame.display.flip()
        gevent.sleep(0)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Client 0.1')
    client = Client(HOST, PORT, tasks, int(arguments["--framerate"]), int(arguments["--x"]), int(arguments["--y"]), int(arguments["--port"]))
    client.start()
    gevent.joinall([
        client,
        gevent.spawn(render, client)
    ])

    pygame.quit()
