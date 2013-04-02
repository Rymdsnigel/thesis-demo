import simplejson as json


def server_event(id, channel, data_id, data_val, timestamp, reserved=None):
    return json.dumps({
    "id": id,
    "channel" : channel,
    "data_id" : data_id,
    "data_val" : data_val,
    "timestamp" : timestamp,
    "reserved" : reserved
    })

def client_response(event_id, timestamp, client_id, state):
    return json.dumps({
    "event_id" : event_id,
    "timestamp" : timestamp,
    "client_id" : client_id,
    "state" : state
    })

def client_info(id, timestamp):
    return json.dumps({
    "client_id" : id,
    "timestamp" : timestamp
    })