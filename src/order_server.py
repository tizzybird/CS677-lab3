from flask import Flask, request, jsonify
import threading
import requests
from datetime import datetime
import json
app = Flask(__name__)
sem = threading.BoundedSemaphore(1)

with open('config.json') as f:
    CONFIG = json.load(f)

HOST_IP = CONFIG['ip']['order']['addr']
HOST_PORT = CONFIG['ip']['order']['port']

CATALOGUE_IP = CONFIG['ip']['catalog']['addr']
CATALOGUE_PORT = CONFIG['ip']['catalog']['port']
CATALOGUE_ADDR = CATALOGUE_IP + ':' + str(CATALOGUE_PORT)

log_buy = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["order_buy"]

# Endpoint for the buy function
@app.route('/buy/<item_no>', methods=['GET'])
def buy(item_no):
    start_time = datetime.now()
    sem.acquire()
    print("Buy request for item " + item_no, file = open('../tests/order_log.txt', 'a'))
    check_availability = requests.get('http://' + CATALOGUE_ADDR + '/lookup/' + item_no)
    check_availability = check_availability.json()
    if(check_availability['stock'] == 0):
        sem.release()
        end_time = datetime.now()
        with open(log_buy, 'a') as f:
            f.write('%f\n' % (end_time - start_time).total_seconds())
        return jsonify({
            'BuyStatus': 'Error',
            'Item': check_availability['book_name'],
            'Reason': 'Item out of stock'
        }), 201

    updated_book = requests.put('http://' + CATALOGUE_ADDR + '/update/' + item_no, json={'stock': check_availability['stock'] - 1})
    sem.release()
    end_time = datetime.now()
    with open(log_buy, 'a') as f:
        f.write('%f\n' % (end_time - start_time).total_seconds())
    return jsonify({
        'BuyStatus': 'Success',
        'Item': updated_book.json()['book_name']
    })

if __name__ == "__main__":
    app.run(host=HOST_IP, port=HOST_PORT, threaded=True)
