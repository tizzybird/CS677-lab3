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
    """
    Create shared information of remote servers.
    :param servers: server information from config.json
    :return: a tuple including an array of static ip information of servers
            and an process-safe object recording server status
    """
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


def choose_server(num):
    """
    Basicly it simply adds 1 to the provided num argument and resets
    the value if num argument is too large
    :param num: process-safe shared variable
    :return: value after added 1
    """
    index = 0
    with num.get_lock():
        index = num.value
        num.value += 1
        if num.value >= reset_value:
            num.value -= reset_value

    return index


def get_server(server_type):
    """
    Choosing a remote server according to load-balancing algorithm.
    Remote servers are chosen evenly.
    :param server_type: the type of remote server, "catalog" or "order"
    :return: return the ip information of the chosen server. If its status
            is UNKNOWN, return None
    """
    servers = order_servers
    num = order_num
    status = order_status
    if server_type == 'catalog':
        servers = catalog_servers
        num = catalog_num
        status = catalog_status

    # still need to modulo total number of servers
    index = choose_server(num) % len(servers)
    server_ip = None
    if status[index]["status"] == ONLINE:
        server_ip = "http://%s:%d/" % (servers[index]["addr"], servers[index]["port"])

    return server_ip


def heartbeat(pairs, logger):
    """
    The function sends TCP echo requests to remote servers and waits for responds.
    If an echo request is timeout, it modifies the corresponding server to UNKNOWN
    status until the server is back ONLINE.
    :param pairs: remote catalog servers and order servers to be monitored
    :param logger: logger
    TODO: Send all heartbeat requests simultaneously with asyncio
    """
    while True:
        for servers, status in pairs:
            for index in range(len(servers)):
                server = servers[index]
                ip = "http://%s:%d/echo" % (server["addr"], server["port"])
                try:
                    res = rq.get(ip, timeout=3)
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

        time.sleep(3)


def start_hearbeat(logger):
    """
    The function will create a background process to monitor the status
    of all remote servers.
    :param logger: logger
    :return: the heartbeat process is returned
    """
    pairs = [(order_servers, order_status), (catalog_servers, catalog_status)]
    # pairs = [(catalog_servers, catalog_status)]
    logger.info("Starting heartbeat demon..")
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
