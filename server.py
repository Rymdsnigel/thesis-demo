# -*- coding: utf-8 -*-
# Server sending events to client
import pygame
import logging
import gevent
import event
from implementations.ntpversion import NTPServer as ServerAlgo
from transports.sockets import SocketServer

logger = logging.getLogger('fisk')
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler(filename='synclog.log')
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


# Handle pygame-inputs
def renderloop(server):

    # Setup pygame
    screen = pygame.display.set_mode((300, 300))
    pygame.display.set_caption("server generating events")
    pygame.init()
    while True:
        e = pygame.event.poll()
        pygame.event.get()
        if e.type == pygame.QUIT:
            break
        if e.type == pygame.MOUSEBUTTONDOWN:
            EVENT = event.create_render_event(id=1,channel=1,data_id=1,data_val=1, timestamp=pygame.time.get_ticks())
            server.broadcast(EVENT)
        if e.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[2]:
                (xpos, ypos) = pygame.mouse.get_pos()
                normalized_pos = ((xpos/300.0), (ypos/300.0))
                EVENT = event.create_render_event(id=1, channel=1, data_id=2, data_val=normalized_pos, timestamp=pygame.time.get_ticks())
                server.broadcast(EVENT)
        screen.fill((0, 0, 0))
        pygame.display.flip()
        gevent.sleep(0)

# Running the server
server = SocketServer('', 5007, ServerAlgo)
gevent.spawn(renderloop, server)
server.serve_forever()



