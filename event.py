def create_latency_update_event(latency, max_latency):
    return {
        "event_type" : 0,
        "latency" : latency,
        "max_latency" : max_latency
    }


def create_sync_event(id, recieved_at=None, sent_at=None, delta=None):
    return {
        "event_type" : 1,
        "recieved_at" :recieved_at,
        "sent_at" : sent_at,
        "delta" : delta,
        "client_id" : id
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



