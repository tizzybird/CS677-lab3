import json
# common config
with open('config.json') as f:
    CONFIG = json.load(f)

# frontend defines
with open('define_frontend.json') as f:
    DEFINE = json.load(f)


import logging
from logging.config import dictConfig

dictConfig(DEFINE['logConfig'])


from flask import Flask, request, jsonify
from datetime import datetime
import requests as rq

import remote, cache

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    start_time = datetime.now()
    ###################################################
    topic_val = request.values.get('topic')
    if topic_val is not None:
        key = repr(('topic', topic_val))
        cache_ret = cache.get(key)
        if cache_ret is not None:
            result = cache_ret
        elif DEFINE["testenv"] == 0:
            res = []
            for item in DEFINE["booklist"]:
                if item["topic"] == topic_val:
                    res.append(item)
            ip = remote.get_server("catalog", app.logger)
            result = jsonify(result=res)
            cache.set_pair(key, result)
        else:
            while True:
                ip = remote.get_server("catalog", app.logger)
                try:
                    res = rq.get(ip + 'search/%s' % topic_val, timeout=DEFINE["timeout"])
                    res.raise_for_status()
                    break
                except:
                    pass

            result = res.json()
            cache.set_pair(key, result)

        end_time = datetime.now()
        diff = (end_time - start_time).total_seconds()

        logging.getLogger('search').info(diff)

        return result

    ###################################################
    lookup_num = request.values.get('lookupNum')
    if lookup_num is not None:
        key = repr(('lookupNum', lookup_num))
        cache_ret = cache.get(key)

        if cache_ret is not None:
            result = cache_ret
        elif DEFINE["testenv"] == 0:
            res = [DEFINE["booklist"][int(lookup_num) - 1]]
            result = jsonify(result=res)
            cache.set_pair(key, result)
        else:
            while True:
                ip = remote.get_server(app.logger)
                try:
                    res = rq.get(ip + 'lookup/%s' % lookup_num)
                    res.raise_for_status()
                    break
                except:
                    pass

            result = res.json()
            cache.set_pair(key, result)
        
        end_time = datetime.now()
        diff = (end_time - start_time).total_seconds()
        
        logging.getLogger('lookup').info(diff)

        return result

    return "Failed", 201


@app.route('/buy', methods=['POST'])
def buy():
    start_time = datetime.now()
    buy_num = request.values.get('buyNum')
    key = repr(('lookupNum', buy_num))

    if DEFINE["testenv"] == 0:
        cache.remove(key)
        return jsonify(result=[DEFINE["booklist"][int(buy_num)]])
    else:
        while True:
            ip = remote.get_server("order", app.logger)
            try:
                res = rq.get(ip + 'buy/%s' % buy_num)
                res.raise_for_status()
                break
            except:
                pass
    
    end_time = datetime.now()
    diff = (end_time - start_time).total_seconds()

    logging.getLogger('buy').info(diff)

    #TODO
    if res.status_code == 200 and res.json()["BuyStatus"] == "Success":
        cache.remove(key)
        return "Success"

    return "Failed", 201


if __name__ == '__main__':
    if DEFINE["testenv"] == 0:
        # proc = remote.start_hearbeat(logging.getLogger('heartbeat'))
        app.run(host="localhost", port="5000", processes=5, threaded=False)
    else:
        proc = remote.start_hearbeat(logging.getLogger('heartbeat'))
        app.run(host=CONFIG["ip"]["frontend"]["addr"],\
            port=CONFIG["ip"]["frontend"]["port"])
        proc.join()
    