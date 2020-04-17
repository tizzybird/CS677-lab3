from flask import Flask, request
from flask import render_template, redirect

from datetime import datetime

import json
import requests as rq

# common config
with open('config.json') as f:
    CONFIG = json.load(f)

# frontend defines
with open('define_frontend.json') as f:
    DEFINE = json.load(f)

ip_catalog = "http://%s:%d/" % (CONFIG["ip"]["catalog"]["addr"], CONFIG["ip"]["catalog"]["port"])
ip_order   = "http://%s:%d/" % (CONFIG["ip"]["order"]["addr"], CONFIG["ip"]["order"]["port"])

log_search = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["frontend_search"]
log_lookup = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["frontend_lookup"]
log_buy    = CONFIG["log_path"]["folder_path"] + CONFIG["log_path"]["frontend_buy"]

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    start_time = datetime.now()
    topic_val = request.values.get('topic')
    lookup_num = request.values.get('lookupNum')
    ###################################################
    # For testing on localhost, please OMIT this part
    if DEFINE["testenv"] == 0:
        if topic_val is None:
            topic_val = ""
        else:
            results = []
            for item in DEFINE["booklist"]:
                if item["topic"] == topic_val:
                    results.append(item)

        if lookup_num is None:
            lookup_num = ""
        else:
            results = [DEFINE["booklist"][int(lookup_num) - 1]]
        
        if request.values.get('withoutUI'):
            end_time = datetime.now()
            diff = (end_time - start_time).total_seconds()
            if topic_val == "":
                with open(log_search, 'a') as f:
                    f.write('%f\n' % diff)
            else:
                with open(log_lookup, 'a') as f:
                    f.write('%f\n' % diff)

            return json.dumps({ "results": results })

        return render_template('homepage.html', results=results, topicVal=topic_val, lookupVal=lookup_num)

    #######################################
    # For invoking micro services
    # for topic searching
    if topic_val is not None:
        res = rq.get(ip_catalog + 'search/%s' % topic_val)

    # for item lookup
    if lookup_num is not None:
        res = rq.get(ip_catalog + 'lookup/%s' % lookup_num)

    # if request.values.get('withoutUI'):
    end_time = datetime.now()
    diff = (end_time - start_time).total_seconds()
    if topic_val is None:
        with open(log_search, 'a') as f:
            f.write('%f\n' % diff)
    else:
        with open(log_lookup, 'a') as f:
            f.write('%f\n' % diff)

    return res.json()


@app.route('/buy', methods=['POST'])
def buy():
    start_time = datetime.now()
    buy_num = request.values.get('buyNum')
    ###################################################
    # For testing on localhost, please OMIT this part
    if DEFINE["testenv"] == 0:
        end_time = datetime.now()
        diff = (end_time - start_time).total_seconds()
        with open(log_buy, 'a') as f:
            f.write('%f\n' % diff)

        if request.values.get('withoutUI'):
            return json.dumps({
                "results": [DEFINE["booklist"][buy_num]]
            })
        
        return redirect('/')

    #######################################
    # For invoking micro services
    res = rq.get(ip_order + 'buy/%s' % buy_num) 

    # if request.values.get('withoutUI'):
    end_time = datetime.now()
    diff = (end_time - start_time).total_seconds()
    with open(log_buy, 'a') as f:
        f.write('%f\n' % diff)
        
    if res.status_code == 200 and res.json()["BuyStatus"] == "Success":
        return "Success"
        
    return "Failed", 201


@app.route('/', methods=['GET'])
def homepage():
    return render_template('homepage.html', isDefault=True, booklist=DEFINE["booklist"])

app.run(host=CONFIG["ip"]["frontend"]["addr"], port=CONFIG["ip"]["frontend"]["port"])