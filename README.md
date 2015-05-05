# Boundary RiskApi Plugin
Boundary Plugin for uWSGI

### Prerequisites
|     OS    | Linux | Windows | SmartOS | OS X |
|:----------|:-----:|:-------:|:-------:|:----:|
| Supported |   v   |         |         |      |

|  Runtime | node.js | Python | Java |
|:---------|:-------:|:------:|:----:|
| Required |         |    +   |      |

### Plugin Setup
None

#### Plugin Configuration Fields
|Field Name   |Description                                                                         |
|:------------|:-----------------------------------------------------------------------------------|
|Poll Interval|The Poll Interval to call the command in milliseconds. Defaults to 1000 milliseconds|

### Metrics Collected
|Metric Name                      |Description                             |
|:--------------------------------|:---------------------------------------|
|UWSGI_WORKER_RSS                 |Resident Set Size                       |
|UWSGI_WORKER_AVG_RT              |Average Request Time                    |
|UWSGI_WORKER_TX                  |Data Transmitted (bytes)                |
|UWSGI_WORKER_REQUESTS            |Number of Requests handled              |
