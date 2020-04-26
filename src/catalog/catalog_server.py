from flask import Flask, request, jsonify, Response
import threading
import requests
from datetime import datetime
import sys
import json
import csv
app = Flask(__name__)
sem = threading.BoundedSemaphore(1)

with open('config.json') as f:
    CONFIG = json.load(f)

HOST_INDEX = int(sys.argv[1])
REPLICA_INDEX = 0 if (HOST_INDEX) else 1

FRONTEND_IP = "http://%s:%d/" % (CONFIG["ip"]["frontend"]["addr"], CONFIG["ip"]["frontend"]["port"])
HOST_IP = CONFIG['ip']['catalog'][HOST_INDEX]['addr']
HOST_PORT = CONFIG['ip']['catalog'][HOST_INDEX]['port']
REPLICA_IP = CONFIG['ip']['catalog'][REPLICA_INDEX]['addr']
REPLICA_PORT = CONFIG['ip']['catalog'][REPLICA_INDEX]['port']
HOST_ADD = HOST_IP + ':' + str(HOST_PORT)
REPLICA_ADD = REPLICA_IP + ':' + str(REPLICA_PORT)

log_req = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["catalog_log"]
log_search = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["catalog_search"]
log_lookup = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["catalog_lookup"]
log_buy    = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["catalog_buy"]



# This is the catalog. Rows are stored as [item_no, book_name, stock, cost, topic]
inventory = []

def sync_inventory():
    global inventory
    try:
        res = requests.get('http://' + REPLICA_ADD + '/sync')
        res.raise_for_status()
        synced_inventory = res.json()['inventory']
        inventory = json.loads(synced_inventory)
    except:
        print("In except")
        catalog = open('catalog/inventory.csv', 'r+')
        catalog = list(csv.reader(catalog))
        for row in catalog:
            tmp = [col.strip() for col in row]
            tmp[0] = int(tmp[0])
            tmp[2] = int(tmp[2])
            tmp[3] = int(tmp[3])
            inventory.append(tmp)

    print(inventory)
    try:
        release = requests.put('http://' + REPLICA_ADD + '/hold', json={ 'instruction': 'release' })
        release.raise_for_status()
    except:
        pass
    return



@app.route('/order_sync', methods = ['GET'])
def order_sync():
    global inventory
    try:
        res = requests.get('http://' + REPLICA_ADD + '/sync')
        res.raise_for_status()
        synced_inventory = res.json()['inventory']
        inventory = json.loads(synced_inventory)
        success = True
    except:
        success = False
    try:
        rel = requests.put('http://' + REPLICA_ADD + '/hold', json={ 'instruction': 'release'})
        rel.raise_for_status()
    except:
        pass
    return jsonify({ 'status': success })



@app.route('/sync', methods=['GET'])
def sync():
    sem.acquire()
    db = json.dumps(inventory)
    return jsonify({ 'inventory': db })



@app.route('/hold', methods=['PUT'])
def hold():
    req =  request.get_json()
    if(req['instruction'] == 'wait'):
        sem.acquire()
        return Response(status=200)
    sem.release()
    return Response(status=200)



# Endpoint for search
@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    start_time = datetime.now()
    with open(log_req, 'a') as f:
        f.write("Incoming search request for topic " + topic)
    sem.acquire()
    result = list(filter(lambda item: item[4] == topic, inventory))
    result = list(map(lambda book: {'item_no': book[0], 'book_name': book[1],'stock': book[2], 'cost': book[3], 'topic': book[4] }, result))
    sem.release()
    with open(log_search, 'a') as f:
        f.write('%f\n' % (datetime.now() - start_time).total_seconds())
    
    return jsonify({
        'books': result
    })



# Endpoint for lookup
@app.route('/lookup/<item_no>', methods=['GET'])
def lookup(item_no):
    start_time = datetime.now()
    with open(log_req, 'a') as f:
        f.write("Incoming lookup request for item " + item_no)
    sem.acquire()
    for books in inventory:
        if(books[0] == int(item_no)):
            res = {
                'book_name': books[1],
                'stock': books[2],
                'cost': books[3]
            }
            break
    sem.release()
    end_time = datetime.now()
    with open(log_lookup, 'a') as f:
        f.write('%f\n' % (end_time - start_time).total_seconds())
    return jsonify(res)



# Endpoint for update
@app.route('/update/<item_no>', methods=['PUT'])
def update(item_no):
    start_time = datetime.now()
    sem.acquire()
    req = request.get_json()
    for books in inventory:
        if(books[0] == int(item_no)):
            if(books[2] >= req['dec']):
                books[2] -= req['dec']
                with open(log_req, 'a') as f:
                    f.write("Stock for item " + item_no + " reduced to " + str(books[2]))

                # cache invalidation
                params = {
                    'item_num': books[0],
                    'topic': books[4]
                }
                requests.put(FRONTEND_IP + 'invalidate', params=params)
                sem.release()
                end_time = datetime.now()
            
                with open(log_buy, 'a') as f:
                    f.write('%f\n' % (end_time - start_time).total_seconds())
            
                return jsonify({'item_no': books[0], 'book_name': books[1],'stock': books[2], 'cost': books[3], 'topic': books[4] })
    
    sem.release()
    return jsonify({}), 201



# Heartbeat
@app.route('/echo', methods=['GET'])
def echo():
    return "OK", 200

if __name__ == '__main__':
    sync_inventory()
    app.run(host=HOST_IP, port=HOST_PORT, threaded=True)
