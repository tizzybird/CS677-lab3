import numpy as np
import json

# common config
with open('config.json') as f:
    CONFIG = json.load(f)

def print_statistics(label, actions, files):
    print('\n\n-------------- %s -------------\n' % label)
    for i in range(len(files)):
        arr = np.loadtxt(CONFIG["log_path"]["folder_path"] + files[i])
        mean = np.mean(arr)
        print('[%s] AVG %s time: %f, total requests: %d\n' % (label, actions[i], mean, len(arr)))


def eval_frontend():
    actions = ['search', 'lookup', 'buy']
    log_frontend = [
        CONFIG["log_path"]["frontend_search"],
        CONFIG["log_path"]["frontend_lookup"],
        CONFIG["log_path"]["frontend_buy"]
    ]
    print_statistics('Frontend', actions, log_frontend)

def eval_catalog():
    # backend
    actions = ['search', 'lookup', 'buy']
    log_catalog = [
        CONFIG["log_path"]["catalog_search"],
        CONFIG["log_path"]["catalog_lookup"],
        CONFIG["log_path"]["catalog_buy"]
    ]
    print_statistics('Catalog', actions, log_catalog)

def eval_order():
    actions_order = ['buy']
    log_order = [CONFIG["log_path"]["order_buy"]]
    print_statistics('Order', actions_order, log_order)

def eval_clients():
    actions = ['search', 'lookup', 'buy']
    print('\n\n-------------- Clients -------------\n')
    arr_total = [np.array([]), np.array([]), np.array([])]
    for i in range(CONFIG["client_numbers"]):
        log_client = [
            CONFIG["log_path"]["client_search"] % i,
            CONFIG["log_path"]["client_lookup"] % i,
            CONFIG["log_path"]["client_buy"] % i
        ]
        for i in range(len(log_client)):
            arr = np.loadtxt(CONFIG["log_path"]["folder_path"] + log_client[i])
            arr_total[i] = np.append(arr_total[i], arr)
    
    for i in range(len(actions)):
        mean = np.mean(arr_total[i])
        print('[Clients] AVG %s time: %f, total requests: %d\n' % (actions[i], mean, len(arr_total[i])))
        # print_statistics('Client %d' % i, actions, log_client)

eval_frontend()
eval_catalog()
eval_order()
eval_clients()
