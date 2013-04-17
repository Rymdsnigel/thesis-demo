#encoding: utf8
import simplejson as json
import pygame
from simplejson.decoder import JSONDecodeError
import gevent
import logging
import event
from transports.sockets import ServerTransport, ClientTransport

max_latency = 0         #todo: om latencyn är för stor så ska klienten hoppa ifatt i animationen ist
logger = logging.getLogger('test')

class NTPServer(ServerTransport):
    # From NTP:
    # t_0 is the time of the request packet transmission
    # t_1 is the time of the request packet reception,
    # t_2 is the time of the response packet transmission
    # t_3 is the time of the response packet reception.

    def send_synchronize(self):
        self.t_0 = pygame.time.get_ticks()      #todo: this is not the actual time we send this, just the time we put it on the queue
        self.queue.put(event.create_sync_event(self.t_0, delta=self.delta))

    def send_latency(self, latency, max_latency):
        self.queue.put(event.create_latency_update_event(latency, max_latency))

    def send_handshake(self):
        self.queue.put(event.create_handshake(self.client_id))

    def send_estate(self, pos):
        self.queue.put(event.create_estate_event(pos))


    def handle_synchronize_response(self, data):
        global max_latency
        self.t_3 = pygame.time.get_ticks()
        self.t_1 = data["recieved_at"]
        self.t_2 = data["sent_at"]
        self.delta = ((self.t_1 - self.t_0) + (self.t_2 - self.t_3))/2
        client_delta = data["delta"]
        if client_delta == 0:       # or client delta differs to much from self.delta
            self.send_synchronize()
        self.latency = (self.t_3 - self.t_0)/2
        if self.latency > max_latency:
            max_latency = self.latency
        self.send_latency(self.latency,max_latency)

    def handle_response(self, data):
        data = json.loads(data)
        if data["event_type"] == 1:
            self.handle_synchronize_response(data)
        elif data["event_type"] == 4:
            self.resolution = data["resolution"]
            # todo calculate new pos
            self.send_estate((0.5, 0,5)(0.5, 0.5))
        else:
            pass

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
                elif data_struct["event_type"] == 3:
                    self.handle_handshake(data_struct)
                elif data_struct["event_type"] == 5:
                    #todo set framesize
                    self.width = data_struct["pos"][0]
                    self.height = data_struct["pos"][1]
                else:
                    self.handle_render_event(data_struct)
            except JSONDecodeError as e:
                print e

    def handle_synchronize(self, data):
        t_1 = pygame.time.get_ticks() # todo: edit actual message to get more exact time
        # todo sleep here to emulate processing
        self.delta = data["delta"]
        t_2 = pygame.time.get_ticks()
        evnt = event.create_sync_event(t_1, t_2, self.delta)
        self.send_packet(evnt)

    def handle_latency(self, data):
        self.latency = data["latency"]
        self.max_latency = data["max_latency"]
        self.applied_latency = self.max_latency - self.latency

    def handle_handshake(self, data):
        self.client_id = data["client_id"]
        logger.handlers[0].setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - ' + str(self.client_id) + '- %(message)s'))
        self.send_packet(event.create_shakeback(100)) #todo should be actual resolution

    def handle_render_event(self, data):
        gevent.sleep(self.applied_latency/1000.0)
        self.queue.put_nowait(data)

    def get_tick(self):
        return pygame.time.get_ticks() - self.delta     # minus because delta negative