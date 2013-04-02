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
#import event as myevent
    
HOST = 'localhost'
PORT = 5007

# Setup pygame
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("client rendering graphics")
pygame.init()

tasks = Queue()
id = ''

# Connect to server
def network():
    s = gevent.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    global id
    id = json.loads(s.recv(1024))["client_id"]
    print id
    while True:
        data = s.recv(1024)
        EVENT = event.client_response(event_id=1, client_id=1, state=1, timestamp=pygame.time.get_ticks())
        s.send(EVENT)
        data_struct = json.loads(data)
        if data_struct["id"] == 1:
            #randis = random.random()*0.0025
            #gevent.sleep(randis)
            tasks.put_nowait(data_struct)
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
            # Compare datatypes here
            data = tasks.get()
            if data["data_id"] == 1:
                color_animation.play(50, 250, 200.0, True, timestamp=pygame.time.get_ticks())
            if data["data_id"] == 2:
                pos = (data["data_val"][0] - rect.left, data["data_val"][1]-rect.top)
                rect = rect.move(pos)
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
