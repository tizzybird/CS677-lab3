from flask import Flask, request, jsonify
from flask import render_template, redirect

from datetime import datetime
# import logging

import json
import requests as rq
import remote

# common config
with open('config.json') as f:
    CONFIG = json.load(f)

# frontend defines
with open('define_frontend.json') as f:
    DEFINE = json.load(f)

# ip_catalog = "http://%s:%d/" % (CONFIG["ip"]["catalog"]["addr"], CONFIG["ip"]["catalog"]["port"])
# ip_order   = "http://%s:%d/" % (CONFIG["ip"]["order"]["addr"], CONFIG["ip"]["order"]["port"])

log_search = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["frontend_search"]
log_lookup = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["frontend_lookup"]
log_buy    = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["frontend_buy"]

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    start_time = datetime.now()
    ###################################################
    topic_val = request.values.get('topic')
    if topic_val is not None:
        if DEFINE["testenv"] == 0:
            res = []
            for item in DEFINE["booklist"]:
                if item["topic"] == topic_val:
                    res.append(item)
            # result = {"result": json.dumps(res)}
            result = jsonify(result=res)
        else:
            ip = remote.get_catalog_ip(app.logger)
            res = rq.get(ip + 'search/%s' % topic_val)
            result = res.json()

        end_time = datetime.now()
        diff = (end_time - start_time).total_seconds()
        with open(log_search, 'a') as f:
            f.write('%f\n' % diff)

        return result

    ###################################################
    lookup_num = request.values.get('lookupNum')
    if lookup_num is not None:
        if DEFINE["testenv"] == 0:
            res = [DEFINE["booklist"][int(lookup_num) - 1]]
            # result = {"result": json.dumps(res)}
            result = jsonify(result=res)
        else:
            ip = remote.get_catalog_ip(app.logger)
            res = rq.get(ip + 'lookup/%s' % lookup_num)
            result = res.json()
        
        end_time = datetime.now()
        diff = (end_time - start_time).total_seconds()
        with open(log_lookup, 'a') as f:
            f.write('%f\n' % diff)

        return result

    return "Failed", 201


@app.route('/buy', methods=['POST'])
def buy():
    start_time = datetime.now()
    buy_num = request.values.get('buyNum')

    if DEFINE["testenv"] == 0:
        return jsonify(result=[DEFINE["booklist"][int(buy_num)]])
    else:
        ip = remote.get_order_ip(app.logger)
        res = rq.get(ip + 'buy/%s' % buy_num)
    
    end_time = datetime.now()
    diff = (end_time - start_time).total_seconds()
    with open(log_buy, 'a') as f:
        f.write('%f\n' % diff)

    #TODO
    if res.status_code == 200 and res.json()["BuyStatus"] == "Success":
        return "Success"

    return "Failed", 201


if __name__ == '__main__':
    if DEFINE["testenv"] == 0:
        app.run(host="localhost", port="5000", processes=2, threaded=False)
    else:
        app.run(host=CONFIG["ip"]["frontend"]["addr"], port=CONFIG["ip"]["frontend"]["port"])
    