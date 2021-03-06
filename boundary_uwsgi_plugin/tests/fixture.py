import json

PARAMS_JSON = """
{
  "uwsgi_poll_interval": "5000"
}
"""

DATA_JSON = """
{
  "version":"2.0.6-debian",
  "listen_queue":0,
  "listen_queue_errors":0,
  "signal_queue":0,
  "load":0,
  "pid":20504,
  "uid":2000,
  "gid":1000,
  "cwd":"/",
  "locks":[
    {
      "user 0":0
    },
    {
      "signal":0
    },
    {
      "filemon":0
    },
    {
      "timer":0
    },
    {
      "rbtimer":0
    },
    {
      "cron":0
    },
    {
      "thunder":20514
    },
    {
      "rpc":0
    },
    {
      "snmp":0
    }
  ],
  "sockets":[
    {
      "name":":3051",
      "proto":"uwsgi",
      "queue":0,
      "max_queue":100,
      "shared":0,
      "can_offload":0
    }
  ],
  "workers":[
    {
      "id":1,
      "pid":20510,
      "accepting":1,
      "requests":9,
      "delta_requests":9,
      "exceptions":0,
      "harakiri_count":0,
      "signals":0,
      "signal_queue":0,
      "status":"idle",
      "rss":124600320,
      "vsz":779878400,
      "running_time":5101223,
      "last_spawn":1430730745,
      "respawn_count":1,
      "tx":684666,
      "avg_rt":1018835,
      "apps":[
        {
          "id":0,
          "modifier1":0,
          "mountpoint":"",
          "startup_time":3,
          "requests":9,
          "exceptions":0,
          "chdir":""
        }
      ],
      "cores":[
        {
          "id":0,
          "requests":3,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        },
        {
          "id":1,
          "requests":3,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        },
        {
          "id":2,
          "requests":3,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        }
      ]
    },
    {
      "id":2,
      "pid":20511,
      "accepting":1,
      "requests":8,
      "delta_requests":8,
      "exceptions":0,
      "harakiri_count":0,
      "signals":0,
      "signal_queue":0,
      "status":"idle",
      "rss":124608512,
      "vsz":780439552,
      "running_time":15414343,
      "last_spawn":1430730745,
      "respawn_count":1,
      "tx":355468,
      "avg_rt":865108,
      "apps":[
        {
          "id":0,
          "modifier1":0,
          "mountpoint":"",
          "startup_time":3,
          "requests":8,
          "exceptions":0,
          "chdir":""
        }
      ],
      "cores":[
        {
          "id":0,
          "requests":3,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        },
        {
          "id":1,
          "requests":2,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        },
        {
          "id":2,
          "requests":3,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        }
      ]
    },
    {
      "id":3,
      "pid":20512,
      "accepting":1,
      "requests":6,
      "delta_requests":6,
      "exceptions":0,
      "harakiri_count":0,
      "signals":0,
      "signal_queue":0,
      "status":"idle",
      "rss":123297792,
      "vsz":779309056,
      "running_time":4279863,
      "last_spawn":1430730745,
      "respawn_count":1,
      "tx":512220,
      "avg_rt":493131,
      "apps":[
        {
          "id":0,
          "modifier1":0,
          "mountpoint":"",
          "startup_time":3,
          "requests":6,
          "exceptions":0,
          "chdir":""
        }
      ],
      "cores":[
        {
          "id":0,
          "requests":2,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        },
        {
          "id":1,
          "requests":2,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        },
        {
          "id":2,
          "requests":2,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        }
      ]
    },
    {
      "id":4,
      "pid":20513,
      "accepting":1,
      "requests":6,
      "delta_requests":6,
      "exceptions":0,
      "harakiri_count":0,
      "signals":0,
      "signal_queue":0,
      "status":"idle",
      "rss":125308928,
      "vsz":780976128,
      "running_time":3758376,
      "last_spawn":1430730745,
      "respawn_count":1,
      "tx":508607,
      "avg_rt":531844,
      "apps":[
        {
          "id":0,
          "modifier1":0,
          "mountpoint":"",
          "startup_time":3,
          "requests":6,
          "exceptions":0,
          "chdir":""
        }
      ],
      "cores":[
        {
          "id":0,
          "requests":2,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        },
        {
          "id":1,
          "requests":2,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        },
        {
          "id":2,
          "requests":2,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        }
      ]
    },
    {
      "id":5,
      "pid":20514,
      "accepting":1,
      "requests":6,
      "delta_requests":6,
      "exceptions":0,
      "harakiri_count":0,
      "signals":0,
      "signal_queue":0,
      "status":"idle",
      "rss":122867712,
      "vsz":779726848,
      "running_time":4010220,
      "last_spawn":1430730745,
      "respawn_count":1,
      "tx":177966,
      "avg_rt":707852,
      "apps":[
        {
          "id":0,
          "modifier1":0,
          "mountpoint":"",
          "startup_time":3,
          "requests":6,
          "exceptions":0,
          "chdir":""
        }
      ],
      "cores":[
        {
          "id":0,
          "requests":2,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        },
        {
          "id":1,
          "requests":2,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        },
        {
          "id":2,
          "requests":2,
          "static_requests":0,
          "routed_requests":0,
          "offloaded_requests":0,
          "write_errors":0,
          "read_errors":0,
          "in_request":0,
          "vars":[
          ]
        }
      ]
    }
  ]
}
"""

SINGLE_WORKER_DATA_JSON = """
{
  "workers":[
    {
      "id":1,
      "requests":9,
      "running_time":5101223,
      "rss":124600320,
      "tx":684666,
      "avg_rt":1018835
    }
  ]
}
"""

SINGLE_WORKER_DATA_DICT = json.loads(SINGLE_WORKER_DATA_JSON)

SINGLE_WORKER_INITIAL_STATE_DATA_JSON = """
{
  "workers":[
    {
      "id":1,
      "requests":0,
      "running_time":0,
      "rss":0,
      "tx":0,
      "avg_rt":0
    }
  ]
}
"""

SINGLE_WORKER_INITIAL_STATE_DATA_DICT = json.loads(SINGLE_WORKER_INITIAL_STATE_DATA_JSON)

MULTIPLE_WORKERS_DATA_JSON = """
{
  "workers":[
    {
      "id":1,
      "requests":9,
      "running_time":5101223,
      "rss":124600320,
      "tx":684666,
      "avg_rt":1018835
    },
    {
      "id":2,
      "requests":8,
      "running_time":4010220,
      "rss":124608512,
      "tx":355468,
      "avg_rt":865108
    }
  ]
}
"""

MULTIPLE_WORKERS_DATA_DICT = json.loads(MULTIPLE_WORKERS_DATA_JSON)
