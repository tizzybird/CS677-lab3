import json
import os
import random

import time
import requests

from threading import Lock
import threading as thd

with open('config.json') as f:
    CONFIG = json.load(f)

with open('define_frontend.json') as f:
    DEFINE = json.load(f)

PRINT_LOCK = Lock()

SEARCH = 1
LOOKUP = 2
BUY    = 3

actions = [SEARCH, LOOKUP, BUY]
ip_frontend = "http://%s:%d/" % (CONFIG["ip"]["frontend"]["addr"], CONFIG["ip"]["frontend"]["port"])

log_search = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["client_search"]
log_lookup = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["client_lookup"]
log_buy    = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["client_buy"]

class Client(thd.Thread):
    def __init__(self, client_id):
        thd.Thread.__init__(self)
        
        self.id = client_id
        self._print("Client %d starts", self.id)
        self.logpath = CONFIG["log_path"]

    def _log(self, msg, filepath):
        filepath = filepath % self.id
        with open(filepath, 'a') as f:
            f.write(msg)

    def _print(self, msg, arg=None):
        with PRINT_LOCK:
            if arg is None:
                print(msg)
            else:
                print(msg % arg)

    def run(self):
        while True:
            action = random.choice(actions)
            
            if action == SEARCH:
                topic = random.choice(list(DEFINE['topics'].values()))
                params = {
                    'topic': topic
                }
                
                self._print('Client %d starts searching topic: %s', arg=(self.id, topic))
                
                start_time = time.time()
                res = requests.get(ip_frontend + 'search', params=params)
                end_time = time.time()
                diff = (end_time - start_time)
                msg = 'Client %d search request success! Time: %f' if res.status_code == 200\
                    else 'Client %d Search request failed! Time: %f'
                
                self._print(msg, arg=(self.id, diff))
                self._log('%f\n' % diff, log_search)

            elif action == LOOKUP:
                item_num = random.randint(1, 4)
                params = {
                    'lookupNum': item_num
                }

                self._print('Client %d starts looking for item: %d', arg=(self.id, item_num))

                start_time = time.time()
                res = requests.get(ip_frontend + 'search', params=params)
                end_time = time.time()
                diff = (end_time - start_time)
                msg = 'Client %d lookup request success! Time: %f' if res.status_code == 200\
                    else 'Client %d lookup request failed! Time: %f'
                
                self._print(msg, arg=(self.id, diff))
                self._log('%f\n' % diff, log_lookup)

            else:
                item_num = random.randint(1, 4)
                params = {
                    'buyNum': item_num
                }

                self._print('Client %d is going to buy item number: %d', arg=(self.id, item_num))
                start_time = time.time()
                res = requests.post(ip_frontend + 'buy', params=params)
                end_time = time.time()
                diff = (end_time - start_time)
                msg = 'Client %d buy request success! Time: %f' if res.status_code == 200\
                    else 'Client %d buy request failed! Time: %f'
                
                self._print(msg, arg=(self.id, diff))
                self._log('%f\n' % diff, log_buy)


if __name__ == '__main__':
    clients = []
    for client_id in range(CONFIG["client_numbers"]):
        client = Client(client_id)
        clients.append(client)
        client.start()

    for client in clients:
        client.join()