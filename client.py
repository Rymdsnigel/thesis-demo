# -*- coding: utf-8 -*-
# Client rendering graphics
import pygame
import gevent
from gevent import socket
from gevent.queue import Queue
import tween
import random
import time
import simplejson as json
import event
    
HOST = 'localhost'
PORT = 5007

# Setup pygame
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("client rendering graphics")
pygame.init()

tasks = Queue()

# Connect to server
def network():
    s = gevent.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    while True:
        data = s.recv(1024)
        data_struct = json.loads(data)
        if data_struct["id"] == 1:
            randis = random.random()*0.0025
            #print randis
            gevent.sleep(randis)
            tasks.put_nowait(data)
        gevent.sleep(0)
    s.close()

# Render
def render():
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
            color_animation.play(50, 250, 200.0, True, timestamp=pygame.time.get_ticks())
        if color_animation.running:
            color_animation.step(pygame.time.get_ticks())
            if int(color_animation.value) <= 255:
                color.b = int(color_animation.value)
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, color, rect)
        pygame.display.flip()
        gevent.sleep(0)

gevent.joinall([
    gevent.spawn(network),
    gevent.spawn(render)
])

pygame.quit()
