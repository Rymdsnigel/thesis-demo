import logging
import time

class Tween(object):

    def __init__(self, *args, **kwargs):
        self.running = False
        self.logger = logging.getLogger('client')


    def play(self, start, end, time=1000.0, reverse=False, interpolation=None, timestamp=None, skip=0):
        self.start = start
        self.end = end
        self.delta = end-start
        self.time = time
        self.timestep = self.delta /self.time
        self.value = start
        self.running = False
        self.reverse = reverse
        self.increasing = (end>start)
        self.running = True
        self.skip = skip
        self.timestamp = timestamp - skip  # this will result in frameskipping if skip is not 0
        self.logger.info("Event animation started")

    def step(self, current_time):
        if self.running :
            diff = current_time - self.timestamp
            self.value += diff * self.timestep
            if (self.value >= self.end) == self.increasing:
                if self.reverse:
                    self.play(self.value, self.start, timestamp=current_time, time=self.time, reverse=False)
                else:
                    self.running = False
                    if self.value > self.end:
                        self.value = self.end
        self.timestamp = current_time


