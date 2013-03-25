# -*- coding: utf-8 -*-
# Server sending events to client
import pygame
import gevent
from gevent import socket
from gevent.event import Event

# Events
EVENT = 'event'

# Socket settings
HOST = ''
PORT = 5007
s = gevent.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

# Setup pygame
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("server generating events")
b = Event()

# Handle connection
def handler(conn, event):
    while True:
        b.wait(timeout=10000)
        conn.sendall(event)
        gevent.sleep(0)
    conn.close()

# Handle pygame-inputs
def renderloop():
    while True:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            b.set()
            b.clear()
    screen.fill((0, 0, 0))
    pygame.display.flip()
    gevent.sleep(0)

# Running the server
try:
    gevent.spawn(renderloop)
    while True:
        conn, addr = s.accept()
        gevent.spawn(handler, conn, EVENT)
except Exception as e:
    print e.message
finally:
    s.close()
