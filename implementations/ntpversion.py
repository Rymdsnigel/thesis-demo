#encoding: utf8
import simplejson as json
import pygame
from simplejson.decoder import JSONDecodeError
import gevent
import logging
import event
from transports.sockets import ServerTransport, ClientTransport

max_latency = 0
logger = logging.getLogger('test')

class NTPServer(ServerTransport):
    # From NTP:
    # t_0 is the time of the request packet transmission
    # t_1 is the time of the request packet reception,
    # t_2 is the time of the response packet transmission
    # t_3 is the time of the response packet reception.

    def send_synchronize(self):
        self.t_0 = pygame.time.get_ticks()      #todo: this is not the actual time we send this, just the time we put it on the queue
        self.queue.put(event.create_sync_event(self.client_id, sent_at=self.t_0, delta=self.delta))

    def send_latency(self, latency, max_latency):
        self.queue.put(event.create_latency_update_event(latency, max_latency))

    def handle_synchronize_response(self, data):
        global max_latency
        self.t_3 = pygame.time.get_ticks()
        self.t_1 = data["recieved_at"]
        self.t_2 = data["sent_at"]
        self.delta = ((self.t_1 - self.t_0) + (self.t_2 - self.t_3))/2
        client_delta = data["delta"]
        client_processing_time = self.t_2 - self.t_1
        self.latency = ((self.t_3 - self.t_0)/2)
        #logging.getLogger("fisk").info("Server: t0: %r, t1: %r, t2: %r t3: %r " % (self.t_0, self.t_1, self.t_2, self.t_3))
        self.handle_max_latency()
        logging.getLogger('fisk').debug("Server: updating client %s latency: (%r - %r)/2 =  %s and max latency: %s  t1: %r, t2: %r " %(self.client_id, self.t_3, self.t_0, self.latency, max_latency, self.t_1, self.t_2))
        if (client_delta == 0) or (abs(client_delta - self.delta) > 2):
            gevent.sleep(0)
            self.send_synchronize()
        self.send_latency(self.latency, max_latency)

    def handle_max_latency(self):
        global max_latency
        if self.latency > max_latency:
            max_latency = self.latency

    def handle_response(self, data):
        data = json.loads(data)
        if data["event_type"] == 1:
            self.handle_synchronize_response(data)

class NTPClient(ClientTransport):

    def handle_incoming(self, data):
        data_list = data.split("\n")
        for item in data_list:
            try:
                data_struct = json.loads(item)
                if data_struct["event_type"] == 1:
                    self.handle_synchronize(data_struct)
                elif data_struct["event_type"] == 0:
                    self.handle_latency(data_struct)
                else:
                    self.handle_render_event(data_struct)
            except JSONDecodeError as e:
                pass
                #print e

    def handle_synchronize(self, data):
        t_1 = self.last_incoming
        if self.client_id == None:
            self.handle_handshake(data["client_id"])
        self.delta = data["delta"]
        t_2 = pygame.time.get_ticks()
        evnt = event.create_sync_event(self.client_id, t_1, t_2, self.delta)
        self.send_packet(evnt)

    def handle_latency(self, data):
        self.latency = data["latency"]
        self.max_latency = data["max_latency"]
        if self.latency >= self.max_latency:
            self.applied_latency = 0
        else:
            self.applied_latency = abs(self.max_latency - self.latency)
        self.logger.info("Client applied latency: %r" % self.applied_latency)

    def handle_handshake(self, client_id):
        self.client_id = client_id
        logger.handlers[0].setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - ' + str(self.client_id) + '- %(message)s'))

    def handle_render_event(self, data):
        gevent.sleep(self.applied_latency/1000.0)
        self.queue.put_nowait(data)

    def get_tick(self):
        return pygame.time.get_ticks() - self.delta     # minus because delta negative