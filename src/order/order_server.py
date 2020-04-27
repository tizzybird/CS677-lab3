from flask import Flask, request, jsonify
import threading
import requests
from datetime import datetime
import json
import sys
app = Flask(__name__)
sem = threading.BoundedSemaphore(1)

with open('config.json') as f:
    CONFIG = json.load(f)

HOST_INDEX = int(sys.argv[1])
REPLICA_INDEX = 0 if (HOST_INDEX) else 1

# Catalog server Addresses
CATALOG0_IP = CONFIG['ip']['catalog'][0]['addr']
CATALOG0_PORT = CONFIG['ip']['catalog'][0]['port']
CATALOG1_IP = CONFIG['ip']['catalog'][1]['addr']
CATALOG1_PORT = CONFIG['ip']['catalog'][1]['port']
CATALOG0_ADD = CATALOG0_IP + ':' + str(CATALOG0_PORT)
CATALOG1_ADD = CATALOG1_IP + ':' + str(CATALOG1_PORT)

# Order Server Addresses
HOST_IP = CONFIG['ip']['order'][HOST_INDEX]['addr']
HOST_PORT = CONFIG['ip']['order'][HOST_INDEX]['port']
REPLICA_IP = CONFIG['ip']['order'][REPLICA_INDEX]['addr']
REPLICA_PORT = CONFIG['ip']['order'][REPLICA_INDEX]['port']
REPLICA_ADD = REPLICA_IP + ':' + str(REPLICA_PORT)

TARGET_CATALOG_ADDR  = CATALOG0_ADD
ALT_CATALOG_ADDR = CATALOG1_ADD

LOCK_ADDR = CONFIG['ip']['lock']['addr'] + ':' + str(CONFIG['ip']['lock']['port'])

log_req = '.' + CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["order_log"]
log_buy = '.' + CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["order_buy"]


# Utitlity function to swap the MASTER and SLAVE statuses of the cataslog server replicas. This is relevant as
# all update requests go to the MASTER and have the SLAVE sync
def swap():
    global TARGET_CATALOG_ADDR
    global ALT_CATALOG_ADDR
    tmp = TARGET_CATALOG_ADDR
    TARGET_CATALOG_ADDR = ALT_CATALOG_ADDR
    ALT_CATALOG_ADDR = tmp
    return





# Endpoint for the buy function
@app.route('/buy/<item_no>', methods=['GET'])
def buy(item_no):
    global TARGET_CATALOG_ADDR
    global ALT_CATALOG_ADDR
    start_time = datetime.now()
    # Obtaining exclusive access via a  distributed lock
    requests.get('http://' + LOCK_ADDR + '/access')
    with open(log_req, 'a') as f:
        f.write("Buy request for item " + item_no)

    # Lookup item at an online catalog server. If the TARGET server is down, the TARGET and ALTERNATE roles
    # are swapped and the request is resent.
    while (True):
        try:
            check_availability = requests.get('http://' + TARGET_CATALOG_ADDR + '/lookup/' + item_no)
            check_availability.raise_for_status()
            break
        except:
            swap()

    if(check_availability.json()['stock'] == 0):
        # Releasing distributed lock
        requests.put('http://' + LOCK_ADDR + '/release')
        end_time = datetime.now()
        with open(log_buy, 'a') as f:
            f.write('%f\n' % (end_time - start_time).total_seconds())
        return jsonify({
            'BuyStatus': 'Error',
            'Item': check_availability.json()['book_name'],
            'Reason': 'Item out of stock'
        }), 201

    # The implementation of an update at both replicas that is resilient to faults. The process is
    # explained in the design doc.
    while (True):
        try:
            purchase = requests.put('http://' + TARGET_CATALOG_ADDR + '/update/' + item_no, json={'dec': 1})
            purchase.raise_for_status()
            try:
                sync = requests.get('http://' + ALT_CATALOG_ADDR + '/order_sync')
                sync.raise_for_status()
                if (sync.json()['status']):
                    break
                else:
                    swap()
                    continue
            except:
                break
        except:
            swap()

    purchase = purchase.json()
    # Release distributed lock
    requests.put('http://' + LOCK_ADDR + '/release')
    end_time = datetime.now()
    with open(log_buy, 'a') as f:
        f.write('%f\n' % (end_time - start_time).total_seconds())
    return jsonify({
        'BuyStatus': 'Success',
        'Item': purchase['book_name']
    })

@app.route('/echo', methods=['GET'])
def echo():
    return "OK", 200

if __name__ == "__main__":
    app.run(host=HOST_IP, port=HOST_PORT, threaded=True)
