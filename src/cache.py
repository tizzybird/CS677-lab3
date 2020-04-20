from multiprocessing import Manager
from datetime import datetime

# cache = Array()
manager = Manager()
cache = manager.dict()
# 300 seconds and the cache will no longer be valid
timeout = 300
# mainly for read operation

def set_pair(key, value):
    cache[key] = {
        "value": value,
        "timestamp": datetime.now()
    }


def get(key):
    res = cache.get(key)
    if res is not None:
        if (datetime.now()-res["timestamp"]).total_seconds() < timeout:
            return res["value"]
        
        del cache[key]

    return None


def remove(key):
    res = cache.get(key)
    if res is not None:
        del cache[key]


def reset():
    cache.clear()