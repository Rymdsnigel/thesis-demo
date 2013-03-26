

class ServerEvent(object):

    def __init__(self, id, channel, data_id, data_val, timestamp, reserved=None):
        self.id = id
        self.channel = channel
        self.data_id = data_id
        self.data_val = data_val
        self.timestamp = timestamp
        self.reserved = reserved


class ClientResponse(object):

    def __init__(self, event_id, timestamp, client_id, state):
        self.event_id = event_id
        self.timestamp = timestamp
        self.client_id = client_id
        self.state = state