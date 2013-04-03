# -*- coding: utf-8 -*-
# Server sending events to client
import pygame
import gevent
from gevent import socket
from gevent.queue import Queue
from gevent.greenlet import Greenlet
import event
import simplejson as json

pool = []

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

class Client(gevent.Greenlet):

    def __init__(self, client_id, conn, delta=0):
        Greenlet.__init__(self)
        #super(gevent.Greenlet, self).__init__()
        self.client_id = client_id
        self.conn = conn
        self.delta = delta
        self.queue = Queue()

    def get_delta(self):
        running = 0
        delta = 0.0
        while True :
            running += 1
            if running >=10:
                break
            id_msg = event.client_info(id=self.client_id, timestamp=pygame.time.get_ticks(), delta=delta)
            self.conn.sendall(id_msg)
            client_reply = json.loads(self.conn.recv(1024))
            delta += (pygame.time.get_ticks() - client_reply["timestamp"])
        self.delta = delta / running       #average delay


    def _run(self):
        self.get_delta()
        while True:
            if not self.queue.empty():
                self.conn.sendall(self.queue.get())            # write event to connection
                data = self.conn.recv(1024)         # wait read
                self.handle_response(data)          # handle data
            gevent.sleep(0)
        self.conn.close()

    def handle_response(self, data):
        print data

    def add_event(self, data):
        self.queue.put(data)

# Handle pygame-inputs
def renderloop():
    while True:
        e = pygame.event.poll()
        pygame.event.get()
        if e.type == pygame.QUIT:
            break
        if e.type == pygame.MOUSEBUTTONDOWN:
            EVENT = event.server_event(id=1,channel=1,data_id=1,data_val=1, timestamp=pygame.time.get_ticks())
            broadcast(EVENT)
        if e.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                EVENT = event.server_event(id=1, channel=1, data_id=2, data_val=pos, timestamp=pygame.time.get_ticks())
                broadcast(EVENT)
        screen.fill((0, 0, 0))
        pygame.display.flip()
        gevent.sleep(0)

# broadcast event to all clients, ugly fix
def broadcast(event):
    for client in pool:
        client.add_event(event)

# Running the server
try:
    gevent.spawn(renderloop)
    client_id = 0
    while True:
        conn, addr = s.accept()
        client_id += 1
        client = Client(client_id, conn)
        client.start()
        pool.append(client)
        gevent.sleep(0)
except Exception as e:
    print e.message
finally:
    s.close()
