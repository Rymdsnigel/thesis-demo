import gevent
import time
import pygame
import logging
from gevent import socket
from gevent.queue import Queue
import simplejson as json


class ServerTransport(gevent.Greenlet):

    def __init__(self, client_id, conn, delta=0):
        gevent.Greenlet.__init__(self)
        self.client_id = client_id
        self.conn = conn
        self.delta = delta
        self.queue = Queue()
        self.logger = logging.getLogger('fisk')
        self.t_0 = 0

    def _run(self):
        self.send_synchronize()
        while True:
            if not self.queue.empty():
                evnt = self.queue.get()
                if evnt["event_type"] == 1:
                    evnt["sent_at"] = pygame.time.get_ticks()
                    self.t_0 = evnt["sent_at"]
                self.logger.info("Server before send")
                gevent.sleep(0)
                self.conn.sendall(json.dumps(evnt)+"\n")            # write event to connection
                self.logger.info("Server after send")
                if evnt["event_type"] == 1:
                    self.logger.info("Server before recv")
                    gevent.sleep()
                    data = self.conn.recv(1024)                     # wait read
                    self.logger.info("Server after recv, data: %s", data)
                    self.handle_response(data)                      # handle data
            gevent.sleep(0)
        self.conn.close()
        self.s.close() #todo remove

    def add_event(self, data):
        self.queue.put(data)

    def send_synchronize(self):
        raise "not implemented"

    def handle_response(self):
        raise "not implemented"


class SocketServer(object):

    def __init__(self, host, port, client_class):
        self.pool = []
        self.host = host
        self.port = port
        self.client_class = client_class
        self.client_count = 0

    # broadcast event to all clients, ugly fix
    def broadcast(self, event):
        for client in self.pool:
            client.add_event(event)

    def serve_forever(self):
        self.s = gevent.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.s.bind((self.host, self.port))
        self.s.listen(5)
        while True:
            try:
                conn, addr = self.s.accept()
                self.client_count += 1
                client = self.client_class(self.client_count, conn)
                client.start()
                self.pool.append(client)
                gevent.sleep(0)
            except Exception as e:
                print e
                self.s.close()

class ClientTransport(gevent.Greenlet):

    def __init__(self, host, port, queue, framerate, pos, width, height, client_port=5007):
        gevent.Greenlet.__init__(self)
        self.host = host
        self.port = port
        self.queue = queue
        self.delta = 0
        self.framerate  = framerate
        self.height = height
        self.width = width
        self.client_port = int(client_port)
        self.client_id = None
        self.pos = pos
        self.skip = 0
        self.applied_latency = 0
        self.logger = logging.getLogger("test")
        self.last_incoming = None

    # Connect to server
    def _run(self):
        self.s = gevent.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.s.bind(('', self.client_port))
        self.s.connect((self.host, self.port))
        while True:
            self.logger.info("Client before recv")
            data = self.s.recv(1024)
            self.logger.info("Client after recv, data: %s", data)
            self.last_incoming = pygame.time.get_ticks()
            self.handle_incoming(data)
            gevent.sleep(0)
        self.s.close()

    def send_packet(self, data):
        self.s.sendall(json.dumps(data))

    def handle_incoming(self, data):
        raise "not implemented"