import json

from multiprocessing import Value

with open('config.json') as f:
    CONFIG = json.load(f)

order_servers = CONFIG['ip']['order']
catalog_servers = CONFIG['ip']['catalog']

reset_value = 999999

order_num = Value('i', 0)
catalog_num = Value('i', 0)

def get_order_ip(logger):
    with order_num.get_lock():
        index = order_num.value
        order_num.value += 1
    
    if order_num.value >= reset_value:
        with order_num.get_lock():
            order_num.value -= reset_value

    index %= len(order_servers)
    res = "http://%s:%d/" % (CONFIG["ip"]["order"][index]["addr"],\
        CONFIG["ip"]["order"][index]["port"])

    logger.debug('order server %d is returned' % (index + 1))

    return res


def get_catalog_ip(logger):
    with catalog_num.get_lock():
        index = catalog_num.value
        catalog_num.value += 1
    
    if catalog_num.value >= reset_value:
        with catalog_num.get_lock():
            catalog_num.value -= reset_value

    index %= len(catalog_servers)
    res = "http://%s:%d/" % (CONFIG["ip"]["catalog"][index]["addr"],\
        CONFIG["ip"]["catalog"][index]["port"])

    logger.debug('catalog server %d is returned' % (index + 1))

    return res
