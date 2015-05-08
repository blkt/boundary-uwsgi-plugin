from StringIO import StringIO
from mock import patch, MagicMock
from nose.tools import (assert_true, assert_equal)

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

    def setUp(self):
        plugin.previous_state = {app: {} for app in plugin.APPS}

    def test_filter_stateless_metric_rss_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested = {key: plugin.STATELESS[key] for key in ["UWSGI_WORKER_RSS"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested, {})

        assert_equal(filtered, {1: {"UWSGI_WORKER_RSS": 124600320}})

    def test_filter_stateless_metric_rss_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested = {key: plugin.STATELESS[key] for key in ["UWSGI_WORKER_RSS"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested, {})

        assert_equal(filtered, {1: {"UWSGI_WORKER_RSS": 124600320},
                                2: {"UWSGI_WORKER_RSS": 124608512}})

    def test_filter_stateful_metric_requests_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested = {key: plugin.STATEFUL[key] for key in ["UWSGI_WORKER_REQUESTS_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested, {})

        assert_equal(filtered, {1: {"UWSGI_WORKER_REQUESTS_DELTA": 9}})

    def test_filter_stateful_metric_requests_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested = {key: plugin.STATEFUL[key] for key in ["UWSGI_WORKER_REQUESTS_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested, {})

        assert_equal(filtered, {1: {"UWSGI_WORKER_REQUESTS_DELTA": 9},
                                2: {"UWSGI_WORKER_REQUESTS_DELTA": 8}})

    def test_filter_stateful_metric_tx_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested = {key: plugin.STATEFUL[key] for key in ["UWSGI_WORKER_TX_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested, {})

        assert_equal(filtered, {1: {"UWSGI_WORKER_TX_DELTA": 684666}})

    def test_filter_stateful_metric_tx_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested = {key: plugin.STATEFUL[key] for key in ["UWSGI_WORKER_TX_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested, {})

        assert_equal(filtered, {1: {"UWSGI_WORKER_TX_DELTA": 684666},
                                2: {"UWSGI_WORKER_TX_DELTA": 355468}})

    def test_filter_metrics_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested_stateless = {key: plugin.STATELESS[key] for key in ["UWSGI_WORKER_RSS"]}
        tested_stateful = {key: plugin.STATEFUL[key]
                           for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested_stateless, tested_stateful)

        assert_equal(filtered, {1: {"UWSGI_WORKER_RSS": 124600320,
                                    "UWSGI_WORKER_REQUESTS_DELTA": 9,
                                    "UWSGI_WORKER_TX_DELTA": 684666}})

    def test_filter_metrics_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested_stateless = {key: plugin.STATELESS[key] for key in ["UWSGI_WORKER_RSS"]}
        tested_stateful = {key: plugin.STATEFUL[key]
                           for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested_stateless, tested_stateful)

        assert_equal(filtered, {1: {"UWSGI_WORKER_RSS": 124600320,
                                     "UWSGI_WORKER_REQUESTS_DELTA": 9,
                                    "UWSGI_WORKER_TX_DELTA": 684666},
                                 2: {"UWSGI_WORKER_RSS": 124608512,
                                     "UWSGI_WORKER_REQUESTS_DELTA":8,
                                     "UWSGI_WORKER_TX_DELTA":355468}})

    def test_filter_stateful_metric_delta_tx_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested = {key: plugin.STATEFUL[key] for key in ["UWSGI_WORKER_TX_DELTA"]}
        first = plugin.filter_metrics("cap", raw_metrics, {}, tested)

        assert_equal(first, {1: {"UWSGI_WORKER_TX_DELTA": 684666}})

        second = plugin.filter_metrics("cap", raw_metrics, {}, tested)

        assert_equal(second, {1: {"UWSGI_WORKER_TX_DELTA": 0}})

    def test_filter_stateful_metric_delta_tx_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested = {key: plugin.STATEFUL[key] for key in ["UWSGI_WORKER_TX_DELTA"]}
        first = plugin.filter_metrics("cap", raw_metrics, {}, tested)

        assert_equal(first, {1: {"UWSGI_WORKER_TX_DELTA": 684666},
                             2: {"UWSGI_WORKER_TX_DELTA":355468}})

        second = plugin.filter_metrics("cap", raw_metrics, {}, tested)

        assert_equal(second, {1: {"UWSGI_WORKER_TX_DELTA": 0},
                              2: {"UWSGI_WORKER_TX_DELTA": 0}})

    def test_filter_complex_stateful_metric_delta_mean_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested = {key: plugin.STATEFUL[key] for key in ["UWSGI_WORKER_AVG_RT_DELTA_POLL"]}
        first = plugin.filter_metrics("cap", raw_metrics, {}, tested)

        assert_equal(first, {1: {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 5101223 / 9}})

        second = plugin.filter_metrics("cap", raw_metrics, {}, tested)

        assert_equal(second, {1: {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 0}})

    def test_filter_complex_stateful_metric_delta_mean_single_worker_zero_division(self):
        raw_metrics = fixture.SINGLE_WORKER_INITIAL_STATE_DATA_DICT
        tested = {key: plugin.STATEFUL[key] for key in ["UWSGI_WORKER_AVG_RT_DELTA_POLL"]}
        first = plugin.filter_metrics("cap", raw_metrics, {}, tested)

        assert_equal(first, {1: {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 0}})

        second = plugin.filter_metrics("cap", raw_metrics, {}, tested)

        assert_equal(second, {1: {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 0}})

    def test_filter_complex_stateful_metric_delta_mean_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested = {key: plugin.STATEFUL[key] for key in ["UWSGI_WORKER_AVG_RT_DELTA_POLL"]}
        first = plugin.filter_metrics("cap", raw_metrics, {}, tested)

        assert_equal(first, {1: {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 5101223 / 9},
                             2: {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 4010220 / 8}})

        second = plugin.filter_metrics("cap", raw_metrics, {}, tested)

        assert_equal(second, {1: {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 0},
                              2: {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 0}})

    def test_report_metrics_single_worker_no_values(self):
        values = {}
        appname = "app"
        hostname = "hostname"
        tested = {key: plugin.STATEFUL[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA"]}
        tested.update({key: plugin.STATELESS[key] for key in ["UWSGI_WORKER_RSS"]})
        timestamp = 1234567890
        expected = ""

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_single_worker_single_value(self):
        values = {1: {"UWSGI_WORKER_REQUESTS_DELTA": 3}}
        appname = "app"
        hostname = "hostname"
        tested = {key: plugin.STATEFUL[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA"]}
        tested.update({key: plugin.STATELESS[key] for key in ["UWSGI_WORKER_RSS"]})
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS_DELTA 3 app-w1@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_single_worker_multiple_values(self):
        values = {1: {"UWSGI_WORKER_REQUESTS_DELTA": 3,
                      "UWSGI_WORKER_TX_DELTA": 3854}}
        appname = "app"
        hostname = "hostname"
        tested = {key: plugin.STATEFUL[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA"]}
        tested.update({key: plugin.STATELESS[key] for key in ["UWSGI_WORKER_RSS"]})
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS_DELTA 3 app-w1@hostname 1234567890\n"
        expected += "UWSGI_WORKER_TX_DELTA 3854 app-w1@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_multiple_workers_single_value(self):
        values = {1: {"UWSGI_WORKER_REQUESTS_DELTA": 3},
                  2: {"UWSGI_WORKER_REQUESTS_DELTA": 3}}
        appname = "app"
        hostname = "hostname"
        tested = {key: plugin.STATEFUL[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA"]}
        tested.update({key: plugin.STATELESS[key] for key in ["UWSGI_WORKER_RSS"]})
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS_DELTA 3 app-w1@hostname 1234567890\n"
        expected += "UWSGI_WORKER_REQUESTS_DELTA 3 app-w2@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_multiple_workers_multiple_values(self):
        values = {1: {"UWSGI_WORKER_REQUESTS_DELTA": 3,
                      "UWSGI_WORKER_TX_DELTA": 3854},
                  2: {"UWSGI_WORKER_REQUESTS_DELTA": 3,
                      "UWSGI_WORKER_TX_DELTA": 13261}}
        appname = "app"
        hostname = "hostname"
        tested = {key: plugin.STATEFUL[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA"]}
        tested.update({key: plugin.STATELESS[key] for key in ["UWSGI_WORKER_RSS"]})
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS_DELTA 3 app-w1@hostname 1234567890\n"
        expected += "UWSGI_WORKER_TX_DELTA 3854 app-w1@hostname 1234567890\n"
        expected += "UWSGI_WORKER_REQUESTS_DELTA 3 app-w2@hostname 1234567890\n"
        expected += "UWSGI_WORKER_TX_DELTA 13261 app-w2@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_multiple_workers_multiple_values(self):
        values = {1: {"UWSGI_WORKER_REQUESTS_DELTA": 3,
                      "UWSGI_WORKER_TX_DELTA": 3854,
                      "UWSGI_WORKER_AVG_RT_DELTA_POLL": 0},
                  2: {"UWSGI_WORKER_REQUESTS_DELTA": 3,
                      "UWSGI_WORKER_TX_DELTA": 13261,
                      "UWSGI_WORKER_AVG_RT_DELTA_POLL": 1}}
        appname = "app"
        hostname = "hostname"
        tested = {key: plugin.STATEFUL[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA"]}
        tested.update({key: plugin.STATELESS[key] for key in ["UWSGI_WORKER_RSS"]})
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS_DELTA 3 app-w1@hostname 1234567890\n"
        expected += "UWSGI_WORKER_TX_DELTA 3854 app-w1@hostname 1234567890\n"
        expected += "UWSGI_WORKER_AVG_RT_DELTA_POLL 0 app-w1@hostname 1234567890\n"
        expected += "UWSGI_WORKER_REQUESTS_DELTA 3 app-w2@hostname 1234567890\n"
        expected += "UWSGI_WORKER_TX_DELTA 13261 app-w2@hostname 1234567890\n"
        expected += "UWSGI_WORKER_AVG_RT_DELTA_POLL 1 app-w2@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_main_loop(self):
        with patch("boundary_uwsgi_plugin.plugin.POLL_INTERVAL", 0):
            with patch("boundary_uwsgi_plugin.plugin.keep_looping_p", side_effect=[True, False]):
                plugin.main()
