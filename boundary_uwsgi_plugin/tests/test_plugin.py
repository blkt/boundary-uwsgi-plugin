from StringIO import StringIO
from mock import patch, call, mock_open, MagicMock
from nose.tools import (assert_true, assert_equal, assert_items_equal)
import time as time

import boundary_uwsgi_plugin.plugin as plugin
import fixture

class TestUtils(object):

    def test_parse_overridden_params(self):
        my_mock = MagicMock()
        with patch("__builtin__.open", my_mock):
            manager = my_mock.return_value.__enter__.return_value
            manager.read.return_value = fixture.PARAMS_JSON
            params = plugin.parse_params()
        expected = {"uwsgi_poll_interval": "5000"}

        assert_equal(params, expected)

    def test_parse_default_params(self):
        my_mock = MagicMock()
        with patch("__builtin__.open", my_mock):
            manager = my_mock.return_value.__enter__.return_value
            manager.read.side_effect = IOError()
            params = plugin.parse_params()
        expected = {}

        assert_equal(params, expected)

    def test_keep_looping_p(self):
        assert_true(plugin.keep_looping_p())

class TestPlugin(object):

    def test_filter_stateless_metric_rss_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        filtered = plugin.filter_metrics(raw_metrics, {"rss": "UWSGI_WORKER_RSS"}, {})

        assert_equal(filtered, {1: {"rss": 124600320}})

    def test_filter_stateless_metric_rss_multiple_worker(self):
        raw_metrics = fixture.MULTIPLE_WORKER_DATA_DICT
        filtered = plugin.filter_metrics(raw_metrics, {"rss": "UWSGI_WORKER_RSS"}, {})

        assert_equal(filtered, {1: {"rss": 124600320}, 2: {"rss": 124608512}})

    def test_filter_stateless_metric_requests_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        filtered = plugin.filter_metrics(raw_metrics, {"requests": "UWSGI_WORKER_REQUESTS"}, {})

        assert_equal(filtered, {1: {"requests": 9}})

    def test_filter_stateless_metric_requests_multiple_worker(self):
        raw_metrics = fixture.MULTIPLE_WORKER_DATA_DICT
        filtered = plugin.filter_metrics(raw_metrics, {"requests": "UWSGI_WORKER_REQUESTS"}, {})

        assert_equal(filtered, {1: {"requests": 9}, 2: {"requests": 8}})

    def test_filter_stateless_metric_tx_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        filtered = plugin.filter_metrics(raw_metrics, {"tx": "UWSGI_WORKER_TX"}, {})

        assert_equal(filtered, {1: {"tx": 684666}})

    def test_filter_stateless_metric_tx_multiple_worker(self):
        raw_metrics = fixture.MULTIPLE_WORKER_DATA_DICT
        filtered = plugin.filter_metrics(raw_metrics, {"tx": "UWSGI_WORKER_TX"}, {})

        assert_equal(filtered, {1: {"tx": 684666}, 2: {"tx": 355468}})

    def test_filter_stateless_metric_avg_rt_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        filtered = plugin.filter_metrics(raw_metrics, {"avg_rt": "UWSGI_WORKER_AVG_RT"}, {})

        assert_equal(filtered, {1: {"avg_rt": 1018835}})

    def test_filter_stateless_metric_avg_rt_multiple_worker(self):
        raw_metrics = fixture.MULTIPLE_WORKER_DATA_DICT
        filtered = plugin.filter_metrics(raw_metrics, {"avg_rt": "UWSGI_WORKER_AVG_RT"}, {})

        assert_equal(filtered, {1: {"avg_rt": 1018835}, 2: {"avg_rt": 865108}})

    def test_filter_stateless_metrics_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        stateless = {"rss": "UWSGI_WORKER_RSS", "avg_rt": "UWSGI_WORKER_AVG_RT"}
        stateful = {"tx": "UWSGI_WORKER_TX", "requests": "UWSGI_WORKER_REQUESTS"}
        filtered = plugin.filter_metrics(raw_metrics, stateless, stateful)

        assert_equal(filtered, {1: {"rss": 124600320,"avg_rt": 1018835,
                                     "requests": 9, "tx": 684666}})

    def test_filter_stateless_metrics_multiple_worker(self):
        raw_metrics = fixture.MULTIPLE_WORKER_DATA_DICT
        stateless = {"rss": "UWSGI_WORKER_RSS", "avg_rt": "UWSGI_WORKER_AVG_RT"}
        stateful = {"tx": "UWSGI_WORKER_TX", "requests": "UWSGI_WORKER_REQUESTS"}
        filtered = plugin.filter_metrics(raw_metrics, stateless, stateful)

        assert_equal(filtered, {1: {"rss": 124600320,"avg_rt": 1018835,
                                     "requests": 9, "tx": 684666},
                                 2: {"rss": 124608512,"avg_rt": 865108,
                                     "requests":8, "tx":355468}})

    def test_report_metrics_single_worker_no_values(self):
        values = {}
        appname = "app"
        hostname = "hostname"
        metrics = {"rss": "UWSGI_WORKER_RSS", "avg_rt": "UWSGI_WORKER_AVG_RT",
                   "tx": "UWSGI_WORKER_TX", "requests": "UWSGI_WORKER_REQUESTS"}
        timestamp = 1234567890
        expected = ""

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  metrics, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_single_worker_single_value(self):
        values = {1: {"requests": 3}}
        appname = "app"
        hostname = "hostname"
        metrics = {"rss": "UWSGI_WORKER_RSS", "avg_rt": "UWSGI_WORKER_AVG_RT",
                   "tx": "UWSGI_WORKER_TX", "requests": "UWSGI_WORKER_REQUESTS"}
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS 3 app-w1@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  metrics, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_single_worker_multiple_value(self):
        values = {1: {"requests": 3, "tx": 3854}}
        appname = "app"
        hostname = "hostname"
        metrics = {"rss": "UWSGI_WORKER_RSS", "avg_rt": "UWSGI_WORKER_AVG_RT",
                   "tx": "UWSGI_WORKER_TX", "requests": "UWSGI_WORKER_REQUESTS"}
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS 3 app-w1@hostname 1234567890\n"
        expected += "UWSGI_WORKER_TX 3854 app-w1@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  metrics, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_multiple_worker_single_value(self):
        values = {1: {"requests": 3}, 2: {'requests': 3}}
        appname = "app"
        hostname = "hostname"
        metrics = {"rss": "UWSGI_WORKER_RSS", "avg_rt": "UWSGI_WORKER_AVG_RT",
                   "tx": "UWSGI_WORKER_TX", "requests": "UWSGI_WORKER_REQUESTS"}
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS 3 app-w1@hostname 1234567890\n"
        expected += "UWSGI_WORKER_REQUESTS 3 app-w2@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  metrics, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_multiple_worker_multiple_value(self):
        values = {1: {"requests": 3, "tx": 3854}, 2: {'requests': 3, 'tx': 13261}}
        appname = "app"
        hostname = "hostname"
        metrics = {"rss": "UWSGI_WORKER_RSS", "avg_rt": "UWSGI_WORKER_AVG_RT",
                   "tx": "UWSGI_WORKER_TX", "requests": "UWSGI_WORKER_REQUESTS"}
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS 3 app-w1@hostname 1234567890\n"
        expected += "UWSGI_WORKER_TX 3854 app-w1@hostname 1234567890\n"
        expected += "UWSGI_WORKER_REQUESTS 3 app-w2@hostname 1234567890\n"
        expected += "UWSGI_WORKER_TX 13261 app-w2@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  metrics, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_main_loop(self):
        with patch("boundary_uwsgi_plugin.plugin.POLL_INTERVAL", 0):
            with patch("boundary_uwsgi_plugin.plugin.keep_looping_p", side_effect=[True, False]):
                plugin.main()
