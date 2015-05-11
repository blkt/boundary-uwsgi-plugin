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
        plugin.METRICS = plugin.init_metrics()

    def test_filter_stateless_metric_rss_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_RSS"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(filtered, {"UWSGI_WORKER_RSS": 124600320})

    def test_filter_stateless_metric_rss_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_RSS"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(filtered, {"UWSGI_WORKER_RSS": 124600320 + 124608512})

    def test_filter_stateful_metric_requests_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_REQUESTS_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(filtered, {"UWSGI_WORKER_REQUESTS_DELTA": 9})

    def test_filter_stateful_metric_requests_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_REQUESTS_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(filtered, {"UWSGI_WORKER_REQUESTS_DELTA": 9 + 8})

    def test_filter_stateful_metric_tx_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_TX_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(filtered, {"UWSGI_WORKER_TX_DELTA": 684666})

    def test_filter_stateful_metric_tx_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_TX_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(filtered, {"UWSGI_WORKER_TX_DELTA": 684666 + 355468})

    def test_filter_metrics_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested = {key: plugin.METRICS[key]
                  for key in ["UWSGI_WORKER_RSS", "UWSGI_WORKER_TX_DELTA",
                              "UWSGI_WORKER_REQUESTS_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(filtered, {"UWSGI_WORKER_RSS": 124600320,
                                "UWSGI_WORKER_REQUESTS_DELTA": 9,
                                "UWSGI_WORKER_TX_DELTA": 684666})

    def test_filter_metrics_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested = {key: plugin.METRICS[key]
                  for key in ["UWSGI_WORKER_RSS", "UWSGI_WORKER_TX_DELTA",
                              "UWSGI_WORKER_REQUESTS_DELTA"]}
        filtered = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(filtered, {"UWSGI_WORKER_RSS": 124600320 + 124608512,
                                "UWSGI_WORKER_REQUESTS_DELTA": 9 + 8,
                                "UWSGI_WORKER_TX_DELTA": 684666 + 355468})

    def test_filter_stateful_metric_delta_tx_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_TX_DELTA"]}
        first = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(first, {"UWSGI_WORKER_TX_DELTA": 684666})

        second = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(second, {"UWSGI_WORKER_TX_DELTA": 0})

    def test_filter_stateful_metric_delta_tx_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_TX_DELTA"]}
        first = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(first, {"UWSGI_WORKER_TX_DELTA": 684666 + 355468})

        second = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(second, {"UWSGI_WORKER_TX_DELTA": 0})

    def test_filter_complex_stateful_metric_delta_mean_single_worker(self):
        raw_metrics = fixture.SINGLE_WORKER_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_AVG_RT_DELTA_POLL"]}
        first = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(first, {"UWSGI_WORKER_AVG_RT_DELTA_POLL": (5101223 / 1000000.0) / 9})

        second = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(second, {"UWSGI_WORKER_AVG_RT_DELTA_POLL": (5101223 / 1000000.0) / 9})

    def test_filter_complex_stateful_metric_delta_mean_single_worker_zero_division(self):
        raw_metrics = fixture.SINGLE_WORKER_INITIAL_STATE_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_AVG_RT_DELTA_POLL"]}
        first = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(first, {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 0})

        second = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(second, {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 0})

    def test_filter_complex_stateful_metric_delta_mean_single_worker_zero_division(self):
        raw_metrics = fixture.SINGLE_WORKER_INITIAL_STATE_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_AVG_RT_DELTA_POLL"]}
        first = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(first, {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 0})

        second = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(second, {"UWSGI_WORKER_AVG_RT_DELTA_POLL": 0})

    def test_filter_complex_stateful_metric_delta_mean_multiple_workers(self):
        raw_metrics = fixture.MULTIPLE_WORKERS_DATA_DICT
        tested = {key: plugin.METRICS[key] for key in ["UWSGI_WORKER_AVG_RT_DELTA_POLL"]}
        first = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(first, {"UWSGI_WORKER_AVG_RT_DELTA_POLL":
                             ((5101223 + 4010220) / 1000000.0) / (9 + 8)})

        second = plugin.filter_metrics("cap", raw_metrics, tested)

        assert_equal(second, {"UWSGI_WORKER_AVG_RT_DELTA_POLL":
                              ((5101223 + 4010220) / 1000000.0) / (9 + 8)})

    def test_report_metrics_single_worker_no_values(self):
        values = {}
        appname = "cap"
        hostname = "hostname"
        tested = {key: plugin.METRICS[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA",
                              "UWSGI_WORKER_RSS"]}
        timestamp = 1234567890
        expected = ""

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_single_worker_single_value(self):
        values = {"UWSGI_WORKER_REQUESTS_DELTA": 3}
        appname = "cap"
        hostname = "hostname"
        tested = {key: plugin.METRICS[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA",
                              "UWSGI_WORKER_RSS"]}
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS_DELTA 3 cap@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_single_worker_multiple_values(self):
        values = {"UWSGI_WORKER_REQUESTS_DELTA": 3, "UWSGI_WORKER_TX_DELTA": 3854}
        appname = "cap"
        hostname = "hostname"
        tested = {key: plugin.METRICS[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA",
                              "UWSGI_WORKER_RSS"]}
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS_DELTA 3 cap@hostname 1234567890\n"
        expected += "UWSGI_WORKER_TX_DELTA 3854 cap@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_multiple_workers_single_value(self):
        values = {"UWSGI_WORKER_REQUESTS_DELTA": 3}
        appname = "cap"
        hostname = "hostname"
        tested = {key: plugin.METRICS[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA",
                              "UWSGI_WORKER_RSS"]}
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS_DELTA 3 cap@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_multiple_workers_2_values(self):
        values = {"UWSGI_WORKER_REQUESTS_DELTA": 3, "UWSGI_WORKER_TX_DELTA": 3854}
        appname = "cap"
        hostname = "hostname"
        tested = {key: plugin.METRICS[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA",
                              "UWSGI_WORKER_RSS"]}
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS_DELTA 3 cap@hostname 1234567890\n"
        expected += "UWSGI_WORKER_TX_DELTA 3854 cap@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_report_metrics_multiple_workers_3_values(self):
        values = {"UWSGI_WORKER_REQUESTS_DELTA": 3, "UWSGI_WORKER_TX_DELTA": 3854,
                  "UWSGI_WORKER_AVG_RT_DELTA_POLL": 0}
        appname = "cap"
        hostname = "hostname"
        tested = {key: plugin.METRICS[key]
                  for key in ["UWSGI_WORKER_TX_DELTA", "UWSGI_WORKER_REQUESTS_DELTA",
                              "UWSGI_WORKER_RSS"]}
        timestamp = 1234567890
        expected = "UWSGI_WORKER_REQUESTS_DELTA 3 cap@hostname 1234567890\n"
        expected += "UWSGI_WORKER_TX_DELTA 3854 cap@hostname 1234567890\n"
        expected += "UWSGI_WORKER_AVG_RT_DELTA_POLL 0 cap@hostname 1234567890\n"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            plugin.report_metrics(values, appname, hostname,
                                  tested, timestamp)

        assert_equal(fake_out.getvalue(), expected)

    def test_main_loop(self):
        with patch("boundary_uwsgi_plugin.plugin.POLL_INTERVAL", 0):
            with patch("boundary_uwsgi_plugin.plugin.keep_looping_p", side_effect=[True, False]):
                plugin.main()
