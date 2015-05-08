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

def gen_identity_func(key):
    def identity(w):
        return w[key]
    return identity

def gen_avg_millis_func(sum_key, card_key):
    def avg(w):
        if w[card_key] != 0:
            return (w[sum_key] / 1000000.0) / w[card_key]
        else:
            return 0
    return avg

# We use abstract unix sockets, so the path has to starts with a null
# byte
DEFAULT_SOCKET_PATH = "\0/uwsgi/{appname}/stats"
APPS = ["cap", "cap-internal", "smweb", "smweb2", "vienna"]

STATELESS = {"UWSGI_WORKER_RSS": gen_identity_func("rss")}
STATEFUL = {"UWSGI_WORKER_TX_DELTA": gen_identity_func("tx"),
            "UWSGI_WORKER_REQUESTS_DELTA": gen_identity_func("requests"),
            "UWSGI_WORKER_AVG_RT_DELTA_POLL": gen_avg_millis_func("running_time", "requests")}

previous_state = {app: {} for app in APPS}

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

def filter_metrics(appname, raw_metrics, stateless_metrics, stateful_metrics):
    """
    "UWSGI_WORKER_RSS": (["rss"], gen_identity_func("rss"))

    """
    acc = {}
    current_state = {}

    for worker in raw_metrics["workers"]:
        iterator = stateless_metrics.iteritems()
        acc[worker["id"]] = {mname: mfunc(worker) for mname, mfunc in iterator}

        worker_previous_state = previous_state[appname].get(worker["id"], {})
        current_state[worker["id"]] = {}

        for mname, mfunc in stateful_metrics.iteritems():
            current_value = mfunc(worker)
            previous_value = worker_previous_state.get(mname, 0)

            if current_value - previous_value >= 0:
                acc[worker["id"]][mname] = current_value - previous_value
            else:
                acc[worker["id"]][mname] = current_value
            current_state[worker["id"]][mname] = current_value

    previous_state[appname] = current_state

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

    UWSGI_WORKER_RSS 12345 app-w1@fqdn 1381857948

    """
    for wid in values:
        vals = values[wid]
        for mname in vals:
            val = vals[mname]
            source = "%s-w%s@%s" % (appname, wid, hostname)
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
    stateless_metrics = STATELESS
    stateful_metrics = STATEFUL
    metrics = stateless_metrics.copy()
    metrics.update(stateful_metrics)

    while keep_looping_p():
        for appname in apps:
            try:
                timestamp = time.time()
                raw_metrics = get_metrics(socket_path, appname, chunk_size)
                values = filter_metrics(appname, raw_metrics, stateless_metrics, stateful_metrics)
                report_metrics(values, appname, hostname, metrics, timestamp=timestamp)
            except ConnectionRefusedError:
                pass # silently fail
            except:
                traceback.print_exc(file=sys.stderr)
        time.sleep(poll_interval)

if __name__ == '__main__':
    main()
