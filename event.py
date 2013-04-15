def create_latency_update_event(latency, max_latency):
    return {
        "event_type" : 0,
        "latency" : latency,
        "max_latency" : max_latency
    }

def create_render_response(event_id, timestamp, client_id, state):  #todo remove? this is never used
    return {
        "event_type" : 1,
        "event_id" : event_id,
        "timestamp" : timestamp,
        "client_id" : client_id,
        "state" : state
    }


def create_handshake(client_id):
    return {
        "event_type" : 3,
        "client_id" : client_id
    }

def create_shakeback(resolution):
    return {
        "event_type" : 4,
        "resolution" : resolution
    }

def create_sync_event(id, recieved_at=None, sent_at=None, delta=None):
    return {
        "event_type" : 1,
        "recieved_at" :recieved_at,
        "sent_at" : sent_at,
        "delta" : delta
    }

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



