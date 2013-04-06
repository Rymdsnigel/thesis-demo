import simplejson as json
import pygame
import event
#from transports.sockets import Server
from transports.sockets import ServerTransport, ClientTransport

class NTPServer(ServerTransport):
    # From NTP:
    # t_0 is the time of the request packet transmission
    # t_1 is the time of the request packet reception,
    # t_2 is the time of the response packet transmission
    # t_3 is the time of the response packet reception.

    def send_synchronize(self):
        self.t_0 = pygame.time.get_ticks()      #todo: this is not the actual time we send this, just the time we put it on the queue
        print "t_0: ", self.t_0
        self.queue.put(event.create_sync_event(self.client_id, self.t_0, delta=self.delta))

    def handle_synchronize_response(self, data):
        self.t_3 = pygame.time.get_ticks()
        self.t_1 = data["recieved_at"]
        self.t_2 = data["sent_at"]
        print "t_3: ", self.t_3
        print "t_2: ", self.t_2
        print "t_1: ", self.t_1
        self.delta = ((self.t_1 - self.t_0) + (self.t_2 - self.t_3))/2
        client_delta = data["delta"]
        if client_delta == 0:       # or client delta differs to much from self.delta
            self.send_synchronize()
        print self.delta

    def handle_response(self, data):
        data = json.loads(data)
        if data["event_type"] == 1:
            self.handle_synchronize_response(data)
        else:
            print data

class NTPClient(ClientTransport):

    def handle_incoming(self, data):
        data_struct = json.loads(data)
        if data_struct["event_type"] == 1:
            self.handle_synchronize(data_struct)
        else:
            print 'inte syncevent'
            self.queue.put_nowait(data_struct)

    def handle_synchronize(self, data):
        t_1 = pygame.time.get_ticks() # todo: edit actual message to get more exact time
        # sleep here to emulate processing
        self.delta = data["delta"]
        t_2 = pygame.time.get_ticks()
        evnt = event.create_sync_event(data["client_id"], t_1, t_2, self.delta)
        self.s.sendall(json.dumps(evnt))

    def get_tick(self):
        return pygame.time.get_ticks() - self.delta #delta negative