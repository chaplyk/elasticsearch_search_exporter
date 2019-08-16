#!/usr/bin/env python
import requests
import json
import time
from prometheus_client import Gauge, start_http_server

try:
    searches_json=open("searches.json", "r").read()
    config=json.loads(searches_json)
    searches=config['searches']
    interval=config['interval']
except ValueError:
    print ("Not valid JSON in searches.json")
    raise
except IOError:
    print ("Configuration file does not exist: searches.json")
    raise
except Exception:
    raise

def get_metrics(search):
        data = json.dumps({"query": searches[search]['query'], "size": 0})
        r = requests.post('http://localhost:9200/_search', data=data).json()
        count = r['hits']['total']
        if not search in g.keys():
            g[search] = Gauge(search, searches[search]['description'])
        g[search].set(count)

if __name__ == '__main__':
    start_http_server(9730)
    g={} # dictionary for Gauges
    while True:
        start = time.time()
        for search in searches:
            try:
                get_metrics(search)
            except Exception as e:
                print ("Cannot retrieve data from ElasticSearch:")
                print (e)
                print ("Retrying in " + str(interval) + " seconds...")
            except KeyboardInterrupt:
                raise
        time.sleep(interval-(time.time()-start))
