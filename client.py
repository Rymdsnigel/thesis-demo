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
  --framerate=<frame/s> Client framerate [default: 0].
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


logger = logging.getLogger('client')
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

#Check if client has closed pygame window
def pygame_running():
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        return False
    else:
        return True

class Animation(object):
    def __init__(self, obj, prop):
        self.obj = obj
        self.prop = prop
        self.tween = tween.Tween()

    def play(self, start, stop, length, reverse, timestamp, skip):
        self.tween.play(start, stop, length, reverse=reverse, timestamp=timestamp, skip=skip)

    def update(self, tick):
        if self.tween.running:
            self.tween.step(tick)
            self.obj[self.prop] = int(tween.value)

class Rectangle(object):
    def __init__(self, client):
        self.color = pygame.Color(100, 110, 50)
        self.color_animation = Animation(obj=self.color, prop='b')
        self.pos = to_local_pos((0.48, 0.5), client.pos)
        self.size = (client.width/10, client.height/10)
        self.client = client
        self.rect = pygame.Rect(to_pixel_pos(self.pos, self.client), self.size)

    def move(self, pos):
        local_pos = to_local_pos(pos, self.client.pos)
        pixel_pos = to_pixel_pos(local_pos, self.lient)
        self.rect.left  = pixel_pos[0]

    def animate(self):
        val = ((1 + math.cos(self.client.get_tick()/250.0))/2)*self.client.height
        self.pos = (0, val - self.rect.top)
        self.rect = self.rect.move(self.pos)
        self.color_animation.update(client.get_tick())

# Render client animation
def render(client):
    screen = pygame.display.set_mode((client.width,client.height))
    pygame.display.set_caption("client rendering graphics")
    pygame.init()
    client.start()
    rect = Rectangle(client)

    while pygame_running():
        if not tasks.empty():
            data = tasks.get()
        else:
            data = {}
        data_id = data.get("data_id", False)

        if data_id == 2: #change position of rect
            rect.move(data[data_val])
        if data_id == 1: #do the coloranimation
            rect.color_animation.play(50, 250, 200.0, True, timestamp=client.get_tick(), skip=client.skip)

        if (client.get_tick() % 1000) == 0:             #This is used to compare how the animations sync between clients when the clients are both running on the same computer
            rect.color_animation.tween.logger.info("Main animation event")

        rect.animate()
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, rect.color, rect.rect)

        pygame.display.flip()
        pygame.time.Clock().tick(client.framerate)
        gevent.sleep(0)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Client 0.1')
    positions = [float(x) for x in arguments["--pos"].split(',')]
    client = Client(HOST, PORT, tasks, int(arguments["--framerate"]), positions, int(arguments["--x"]), int(arguments["--y"]), int(arguments["--port"]))
    gevent.joinall([
        client,
        gevent.spawn(render, client)
    ])

    pygame.quit()
