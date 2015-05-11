import json
import socket
import sys
import time
import traceback

import logging
log = logging.getLogger(__name__)

HOSTNAME = socket.getfqdn()
POLL_INTERVAL = 1000
DEFAULT_CHUNK_SIZE = 4096

class gen_dispatcher_on(object):

    def __init__(self, keys, func):
        self.keys = keys
        self.func = func
        self.func_set = {key: func for key in keys}

    def __call__(self, key):
        return self.func_set[key]

class gen_identity_func(object):

    def __init__(self, key):
        self.key = key

    def __call__(self, ws):
        res = 0

        for w in ws:
            res += w[self.key]

        return res

class gen_delta_identity_func(object):

    def __init__(self, key):
        self.previous_value = 0
        self.key = key

    def __call__(self, ws):
        current_value = 0

        for w in ws:
            current_value += w[self.key]

        res = current_value - self.previous_value
        self.previous_value = res
        return res

class gen_avg_millis_func(object):

    def __init__(self, sum_key, card_key):
        self.previous_value = 0
        self.prev_sum_val = 0
        self.prev_card_val = 0
        self.sum_key = sum_key
        self.card_key = card_key

    def __call__(self, ws):
        res = 0

        curr_sum_val = 0
        curr_card_val = 0

        for w in ws:
            curr_sum_val += w[self.sum_key]
            curr_card_val += w[self.card_key]

        delta_sum_val = curr_sum_val - self.prev_sum_val
        delta_card_val = curr_card_val - self.prev_card_val

        if delta_card_val != 0:
            res = (delta_sum_val / 1000000.0) / delta_card_val
            self.previous_value = res
            return res
        else:
            return self.previous_value

def init_metrics():
    return {"UWSGI_WORKER_RSS": gen_dispatcher_on(APPS, gen_identity_func("rss")),
            "UWSGI_WORKER_TX_DELTA": gen_dispatcher_on(APPS, gen_delta_identity_func("tx")),
            "UWSGI_WORKER_REQUESTS_DELTA": gen_dispatcher_on(APPS, gen_delta_identity_func("requests")),
            "UWSGI_WORKER_AVG_RT_DELTA_POLL": gen_dispatcher_on(APPS, gen_avg_millis_func("running_time", "requests"))}

# We use abstract unix sockets, so the path has to starts with a null
# byte
DEFAULT_SOCKET_PATH = "\0/uwsgi/{appname}/stats"
APPS = ["cap", "cap-internal", "smweb", "smweb2", "vienna"]

METRICS = init_metrics()

class ConnectionRefusedError(Exception):
    pass

def parse_params():
    """Parses and returns the contents of the plugin's "param.json" file.

    """
    plugin_params = dict()
    try:
        with open("param.json") as f:
            plugin_params = json.load(f)
    except IOError:
        pass
    return plugin_params

def get_metrics(socket_path, appname, chunk_size):
    """Returns a Python dictionary.

    """
    path = socket_path.format(appname=appname)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    try:
        sock.connect(path)
    except socket.error as e:
        if e.errno == socket.errno.ECONNREFUSED:
            raise ConnectionRefusedError()
        else:
            raise

    chunks = []
    while True:
        chunk = sock.recv(chunk_size)
        if not chunk:
            break
        chunks.append(chunk)
    sock.close()

    res = json.loads("".join(chunks))
    return res

def filter_metrics(appname, raw_metrics, metrics):
    """
    "UWSGI_WORKER_RSS": gen_identity_func("rss")

    """
    acc = {}

    for metric, dispatcher in metrics.iteritems():
        calculator = dispatcher(appname)
        acc[metric] = calculator(raw_metrics["workers"])

    return acc

def report_metrics(values, appname, hostname, metrics, timestamp=None):
    """Prints the given metrics (pairs of strings and numbers) to
    standard output appending the hostname and, optionally, the
    timestamp.

    {1: {'requests': 3, 'tx': 3854},
     2: {'requests': 3, 'tx': 13261},
     3: {'requests': 2, 'tx': 169791},
     4: {'requests': 3, 'tx': 170804},
     5: {'requests': 3, 'tx': 170597}}

    UWSGI_WORKER_RSS 12345 app@fqdn 1381857948

    """
    for mname in values:
        val = values[mname]
        source = "%s@%s" % (appname, hostname)
        msg = "%s %s %s%s" % (mname, val, source,
                              (" %d" % timestamp) if timestamp else "")
        print msg
        sys.stdout.flush()

def keep_looping_p():
    return True

def main():
    """Extracts raw metrics, flattens them, boundarifies their metrics
    name, and writes them to standard output once every POLL_INTERVAL
    milliseconds.

    """
    params = parse_params()
    poll_interval = int(params.get("uwsgi_poll_interval", POLL_INTERVAL) / 1000)

    hostname = HOSTNAME
    apps = APPS
    socket_path = DEFAULT_SOCKET_PATH
    chunk_size = DEFAULT_CHUNK_SIZE
    metrics = METRICS

    while keep_looping_p():
        for appname in apps:
            try:
                timestamp = time.time()
                raw_metrics = get_metrics(socket_path, appname, chunk_size)
                values = filter_metrics(appname, raw_metrics, metrics)
                report_metrics(values, appname, hostname, metrics, timestamp=timestamp)
            except ConnectionRefusedError:
                pass # silently fail
            except:
                traceback.print_exc(file=sys.stderr)
        time.sleep(poll_interval)

if __name__ == '__main__':
    main()
