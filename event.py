import simplejson as json


def create_render_event(id, channel, data_id, data_val, timestamp, reserved=None):
    return {
    "event_type" : 2,
    "id": id,
    "channel" : channel,
    "data_id" : data_id,
    "data_val" : data_val,
    "timestamp" : timestamp,
    "reserved" : reserved
    }

def create_render_response(event_id, timestamp, client_id, state):
    return {
    "event_type" : 1,
    "event_id" : event_id,
    "timestamp" : timestamp,
    "client_id" : client_id,
    "state" : state
    }

def create_sync_event( id, recieved_at=None, sent_at=None, delta=None):
    return {
    "event_type" : 1,
    "client_id" : id,
    "recieved_at" :recieved_at,
    "sent_at" : sent_at,
    "delta" : delta
    }