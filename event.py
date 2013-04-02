import simplejson as json

class Event(object):

    def server_event(self, id, channel, data_id, data_val, timestamp, reserved=None):
        return json.dumps({
        "id": id,
        "channel" : channel,
        "data_id" : data_id,
        "data_val" : data_val,
        "timestamp" : timestamp,
        "reserved" : reserved
        })

    def client_response(self, event_id, timestamp, client_id, state):
        return json.dumps({
        "event_id" : event_id,
        "timestamp" : timestamp,
        "client_id" : client_id,
        "state" : state
        })

    def client_info(self, id, timestamp):
        return json.dumps({
        "id" : id,
        "timestamp" : timestamp
        })