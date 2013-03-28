# -*- coding: utf-8 -*-
# Server sending events to client
import pygame
import gevent
from gevent import socket
from gevent.event import Event
from gevent.event import AsyncResult
import event
import simplejson as json

b = Event()
EVENT = "abs"
#b.clear()

# Socket settings
HOST = ''
PORT = 5007
s = gevent.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

# Setup pygame
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("server generating events")
pygame.init()



# Handle connection
def handler(conn):
    while True:
        b.wait(timeout=10000)
        #print 'sending event: ', EVENT
        conn.sendall(EVENT)
        gevent.sleep(0)
    conn.close()

# Handle pygame-inputs
def renderloop():
    while True:
        global EVENT
        e = pygame.event.poll()
        pygame.event.get()
        if e.type == pygame.QUIT:
            break
        if e.type == pygame.MOUSEBUTTONDOWN:
            server_event = event.ServerEvent(id=1,channel=1,data_id=1,data_val=1, timestamp=pygame.time.get_ticks())
            EVENT = json.dumps(server_event.__dict__)
            b.set()
            b.clear()
        if e.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                move_event = event.ServerEvent(id=1, channel=1, data_id=2, data_val=pos, timestamp=pygame.time.get_ticks())
                EVENT = json.dumps(move_event.__dict__)
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
        gevent.spawn(handler, conn)
        gevent.sleep(0)
except Exception as e:
    print e.message
finally:
    s.close()
