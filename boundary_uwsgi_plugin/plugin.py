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

DEFAULT_SOCKET_PATH = "/var/run/{appname}/stats.sock"
APPS = ["cap", "cap-internal", "smweb", "smweb2", "vienna"]
STATELESS = {"rss": "UWSGI_WORKER_RSS", "avg_rt": "UWSGI_WORKER_AVG_RT"}
STATEFUL = {"tx": "UWSGI_WORKER_TX", "requests": "UWSGI_WORKER_REQUESTS"}
METRICS = dict(STATELESS).update(STATEFUL)

previous_state = {}

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
    sock.connect(path)

    chunks = []
    while True:
        chunk = sock.recv(chunk_size)
        if not chunk:
            break
        chunks.append(chunk)

    res = json.loads("".join(chunks))
    return res

def filter_metrics(raw_metrics, stateless_metrics, stateful_metrics):
    global previous_state
    acc = {}

    for worker in raw_metrics["workers"]:
        metrics = {key: worker[key] for key in stateless_metrics}
        tmp = acc.get(worker["id"], {})
        acc[worker["id"]] = metrics

    for worker in raw_metrics["workers"]:
        worker_previous_state = previous_state.get(worker["id"], {})
        current_state = {}
        metrics = {}

        for key in stateful_metrics:
            current_value = worker[key]
            previous_value = worker_previous_state.get(key, 0)
            current_state[key] = worker[key]
            metrics[key] = max(current_value, current_value - previous_value)

        tmp = acc.get(worker["id"], {})
        if tmp:
            acc.get(worker["id"]).update(metrics)
        else:
            acc[worker["id"]] = metrics

        previous_state.get(worker["id"], {}).update(current_state)

    return acc

def report_metrics(values, appname, hostname, metrics, timestamp=None):
    """Prints the given metrics (pairs of strings and numbers) to standard
    output appending the hostname and, optionally, the timestamp.

    {1: {'requests': 3, 'tx': 3854},
     2: {'requests': 3, 'tx': 13261},
     3: {'requests': 2, 'tx': 169791},
     4: {'requests': 3, 'tx': 170804},
     5: {'requests': 3, 'tx': 170597}}

    UWSGI_WORKER_RSS 12345 app-w1@fqdn 1381857948

    """
    for wid in values:
        vals = values[wid]
        for key in vals:
            val = vals[key]
            source = "%s-w%s@%s" % (appname, wid, hostname)
            msg = "%s %s %s%s" % (metrics[key], val, source,
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
    metrics = METRICS

    while keep_looping_p():
        for appname in apps:
            try:
                timestamp = time.time()
                raw_metrics = get_metrics(socket_path, appname, chunk_size)
                values = filter_metrics(raw_metrics, stateless_metrics, stateful_metrics)
                report_metrics(values, appname, hostname, metrics, timestamp=timestamp)
            except:
                traceback.print_exc(file=sys.stderr)
        time.sleep(poll_interval)

if __name__ == '__main__':
    main()
