from flask import Flask, request, jsonify
import threading
from datetime import datetime
import sys
import json
import csv
app = Flask(__name__)
sem = threading.BoundedSemaphore(1)

with open('config.json') as f:
    CONFIG = json.load(f)

HOST_IP = CONFIG['ip']['catalog']['addr']
HOST_PORT = CONFIG['ip']['catalog']['port']

log_search = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["catalog_search"]
log_lookup = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["catalog_lookup"]
log_buy    = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["catalog_buy"]

# This is the catalog. Rows are stored as [item_no, book_name, stock, cost, topic]
catalog_file = sys.argv[1]
catalog = open(catalog_file, 'r+')
catalog = list(csv.reader(catalog))

# Preprocessing on the input catalog
inventory = []

for row in catalog:
    tmp = [col.strip() for col in row]
    tmp[0] = int(tmp[0])
    tmp[2] = int(tmp[2])
    tmp[3] = int(tmp[3])
    inventory.append(tmp)


# Endpoint for search
@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    start_time = datetime.now()
    print("Incoming search request for topic " + topic, file=open('../tests/catalog_log.txt', 'a'))
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
    print("Incoming lookup request for item " + item_no, file=open('../tests/catalog_log.txt', 'a'))
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
            books[2] = req['stock']
            print("Stock for item " + item_no, "reduced to " + str(req['stock']), file = open('../tests/catalog_log.txt', 'a'))
            sem.release()
            end_time = datetime.now()
            
            with open(log_buy, 'a') as f:
                f.write('%f\n' % (end_time - start_time).total_seconds())
            
            return jsonify({'item_no': books[0], 'book_name': books[1],'stock': books[2], 'cost': books[3], 'topic': books[4] })
    
    sem.release()
    return jsonify({}), 201


if __name__ == '__main__':
    app.run(host=HOST_IP, port=HOST_PORT, threaded=True)
