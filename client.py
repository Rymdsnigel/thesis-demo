# -*- coding: utf-8 -*-
# Client rendering graphics
import pygame
import gevent
from gevent.queue import Queue
import math
import tween
from implementations.ntpversion import NTPClient as Client


HOST = 'localhost'
PORT = 5007

# Setup pygame
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("client rendering graphics")
pygame.init()

tasks = Queue()
id = ''

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
            print "renderevent: ", data
            if data["data_id"] == 1:
                color_animation.play(50, 250, 200.0, True, timestamp=pygame.time.get_ticks())
            if data["data_id"] == 2:
                pos = (data["data_val"][0] - rect.left, 0)
                rect = rect.move(pos)
        if color_animation.running:
            color_animation.step(pygame.time.get_ticks())
            if int(color_animation.value) <= 255:
                color.b = int(color_animation.value)

        val = ((1 + math.cos(client.get_tick()/250.0))/2)*250
        pos = (0, val - rect.top)
        rect = rect.move(pos)
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, color, rect)
        pygame.display.flip()
        gevent.sleep(0)

client = Client(HOST, PORT, tasks)
client.start()
gevent.joinall([
    client,
    gevent.spawn(render, client)
])

pygame.quit()
