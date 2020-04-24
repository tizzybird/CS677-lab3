from flask import Flask, request, jsonify, Response
import requests
import threading
import json
app = Flask(__name__)
access_sem = threading.BoundedSemaphore(1)


with open('config.json') as f:
    CONFIG = json.load(f)

HOST_IP = CONFIG['ip']['lock']['addr']
HOST_PORT = CONFIG['ip']['lock']['port']

@app.route('/access', methods=['GET'])
def access():
    access_sem.acquire(timeout=2)
    return jsonify({
        'status': 'acquired'
    })

@app.route('/release', methods=['PUT'])
def release():
    access_sem.release()
    return jsonify({
        'status': 'released'
    })

if __name__ == "__main__":
    app.run(host=HOST_IP, port = int(HOST_PORT), threaded=True)