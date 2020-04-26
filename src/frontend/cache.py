from multiprocessing import Manager
from datetime import datetime

# only for read operation
manager = Manager()
cache = manager.dict()
# Timeout value that cached values would no longer be valid
timeout = 180

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