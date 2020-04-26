import json

# common config
with open('../config.json') as f:
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
    """
    Function for responding topic searching and item lookup
    :param topic: searching by a specific topic
    :param lookupNum: lookup information of a specific item id
    :return: a json object if success, otherwise a failed message
    """
    cache_ret = None
    is_from_cache = False
    start_time = datetime.now()
    ###################################################
    # topic searching
    topic_val = request.values.get('topic')
    if topic_val is not None:
        key = repr(('topic', topic_val))
        if DEFINE['withCache'] == 1:
            cache_ret = cache.get(key)
        
        if cache_ret is not None:
            result = cache_ret
            is_from_cache = True
            app.logger.info("[Cache] Return cached value: %s", result)
        elif DEFINE["testenv"] == 0:
            res = []
            for item in DEFINE["booklist"]:
                if item["topic"] == topic_val:
                    res.append(item)
            result = jsonify(result=res)
        else:
            failureCount = 0
            while failureCount < 5:
                ip = remote.get_server("catalog")
                failureCount += 1
                
                if ip is None:
                    app.logger.info("Cannot get a catalog server IP; retry time(s): %d" % failureCount)
                    continue
                try:
                    res = rq.get(ip + 'search/%s' % topic_val, timeout=5)
                    res.raise_for_status()
                    break
                except:
                    app.logger.info("Catalog server is timeout; retry time(s): %d" % failureCount)
            
            # if failed, return failure
            # clear cache, abort recording time
            if failureCount >= 5:
                cache.remove(key)
                end_time = datetime.now()
                diff = (end_time - start_time).total_seconds()
                logging.getLogger('search').info("Failed, %s" % diff)

                return "Failed", 201

            result = res.json()
        
        #-------------------------------
        if DEFINE['withCache'] == 1 and not is_from_cache:
            app.logger.info("[Cache] Set cache: %s", result)
            cache.set_pair(key, result)

        end_time = datetime.now()
        diff = (end_time - start_time).total_seconds()
        logging.getLogger('search').info("Success, %s" % diff)

        return result

    ###################################################
    # item information lookup
    lookup_num = request.values.get('lookupNum')
    if lookup_num is not None:
        key = repr(('lookupNum', lookup_num))
        if DEFINE['withCache'] == 1:
            cache_ret = cache.get(key)

        if cache_ret is not None:
            result = cache_ret
            is_from_cache = True
            app.logger.info("[Cache] Return cached value: %s", result)
        elif DEFINE["testenv"] == 0:
            res = [DEFINE["booklist"][int(lookup_num) - 1]]
            result = jsonify(result=res)
        else:
            failureCount = 0
            while failureCount < 5:
                ip = remote.get_server("catalog")
                failureCount += 1
                
                if ip is None:
                    app.logger.info("Cannot get a catalog server IP; retry time(s): %d" % failureCount)
                    continue
                try:
                    res = rq.get(ip + 'lookup/%s' % lookup_num, timeout=5)
                    res.raise_for_status()
                    break
                except:
                    app.logger.info("Catalog server is timeout; retry time(s): %d" % failureCount)

            # if failed, return failure
            # clear cache, abort recording time
            if failureCount >= 5:
                cache.remove(key)
                end_time = datetime.now()
                diff = (end_time - start_time).total_seconds()
                logging.getLogger('lookup').info("Failed, %s" % diff)

                return "Failed", 201

            result = res.json()

        #-------------------------------
        if DEFINE['withCache'] == 1 and not is_from_cache:
            app.logger.info("[Cache] Set cache: %s", result)
            cache.set_pair(key, result)

        end_time = datetime.now()
        diff = (end_time - start_time).total_seconds()
        logging.getLogger('lookup').info("Success, %s" % diff)

        return result

    return "Failed", 201


@app.route('/buy', methods=['POST'])
def buy():
    """
    Function for handling buy requests
    :param buyNum: buy a book with item id
    :return: return failed message when item id is none or order servers are offline,
            otherwise a success message is returned
    """
    start_time = datetime.now()
    buy_num = request.values.get('buyNum')

    if buy_num is None:
        return "Failed", 201

    if DEFINE["testenv"] == 0:    
        return jsonify(result=[DEFINE["booklist"][int(buy_num)]])

    res = None
    failureCount = 0
    while failureCount < 5:
        ip = remote.get_server("order")
        failureCount += 1
        if ip is None:
            app.logger.info("Cannot get an order server IP; retry time(s): %d" % failureCount)
            continue
        try:
            res = rq.get(ip + 'buy/%s' % buy_num, timeout=5)
            res.raise_for_status()
            break
        except:
            app.logger.info("Order server is timeout; retry time(s): %d" % failureCount)

    
    end_time = datetime.now()
    diff = (end_time - start_time).total_seconds()

    if res is not None and res.status_code == 200 and res.json()["BuyStatus"] == "Success":
        logging.getLogger('buy').info("Success, %s" % diff)
        return "Success"

    logging.getLogger('buy').info("Failed, %s" % diff)
    return "Failed", 201


@app.route('/invalidate', methods=['PUT'])
def invalidate():
    """
    Delete specified item from cache.
    :param item_num: item id
    :param topic: topic
    :return: always return success
    """
    item_num  = request.values.get('item_num')
    if item_num is not None:
        key = repr(('lookupNum', item_num))
        cache.remove(key)
        app.logger.info("[Cache]-------------------- Remove %s" % key)
    
    topic_val = request.values.get('topic')
    if topic_val is not None:
        key = repr(('topic', topic_val))
        cache.remove(key)
        app.logger.info("[Cache]-------------------- Remove %s" % key)

    return "Success"


if __name__ == '__main__':
    # start heartbeat protocol
    proc = remote.start_hearbeat(logging.getLogger('heartbeat'))
    
    if DEFINE["testenv"] == 0:
        app.run(host="localhost", port="5000", processes=5, threaded=False)
    else:
        app.run(host=CONFIG["ip"]["frontend"]["addr"], port=CONFIG["ip"]["frontend"]["port"])
        proc.join()
    