import json

from multiprocessing import Value, Manager
import multiprocessing as mp

# import asyncio
import requests as rq
import time

UNKNOWN = 0
ONLINE  = 1

reset_value = 999999

########################################

def init(servers):
    # shared server status information
    manager = Manager()
    obj = manager.dict()
    # normal static server information
    result = []
    count = 0
    for server in servers:
        result.append({
            "addr": server["addr"],
            "port": server["port"]
        })
        obj[count] = {
            "status": UNKNOWN,
            "retry": 0
        }
        count += 1

    return result, obj


def choose_server(servers, num):
    index = 0
    with num.get_lock():
        index = num.value
        num.value += 1
        if num.value >= reset_value:
            num.value -= reset_value

    return index


def get_server(server_type, logger=None):
    servers = order_servers
    num = order_num
    status = order_status
    if server_type == 'catalog':
        servers = catalog_servers
        num = catalog_num
        status = catalog_status

    while True:
        index = choose_server(servers, num) % len(servers)
        if status[index]["status"] == ONLINE:
            break

    server_ip = "http://%s:%d/" % (servers[index]["addr"], servers[index]["port"])

    if logger is not None:
        logger.debug(server_type, ' server is returned: %s' % server_ip)

    return server_ip


def heartbeat(pairs, logger):
    # TODO: asyncio
    # loop = asyncio.get_event_loop()
    # async def ping(ip, index, proxy):
    #     res = await loop.run_in_executor(None, requests.get, url)

    while True:
        for servers, status in pairs:
            for index in range(len(servers)):
                server = servers[index]
                ip = "http://%s:%d/echo" % (server["addr"], server["port"])
                try:
                    res = rq.get(ip, timeout=5)
                    res.raise_for_status()
                    status[index] = {
                        "status": ONLINE,
                        "retry": 0
                    }
                except:
                    status[index] = {
                        "status": UNKNOWN,
                        "retry": status[index]["retry"] + 1
                    }
                
                logger.info("%s - status: %s" % (ip, repr(status[index])))

        time.sleep(4)


def start_hearbeat(logger):
    pairs = [(order_servers, order_status), (catalog_servers, catalog_status)]
    logger.warning("Starting heartbeat demon..")
    proc = mp.Process(target=heartbeat, args=(pairs, logger))
    proc.start()

    return proc


################################
order_num = Value('i', 0)
catalog_num = Value('i', 0)

with open('config.json') as f:
    CONFIG = json.load(f)

order_servers, order_status = init(CONFIG['ip']['order'])
catalog_servers, catalog_status = init(CONFIG['ip']['catalog'])
