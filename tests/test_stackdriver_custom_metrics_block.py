from unittest.mock import patch, MagicMock
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..stackdriver_custom_metrics_block import StackdriverCustomMetrics


class TestStackdriverCustomMetrics(NIOBlockTestCase):

    def _test(self, signals, config=None):
        config = config or {}
        block = StackdriverCustomMetrics()
        metric_type = config.get('metric_type', 'custom.googleapis.com/metric')
        with patch(block.__module__ + '.monitoring') as monitoring:
            client = MagicMock()
            metric = MagicMock()
            client.metric.return_value = metric
            resource = MagicMock()
            client.resource.return_value = resource
            monitoring.Client.return_value = client
            self.configure_block(block, config)
            block.start()
            block.process_signals(signals)
            block.stop()
        self.assert_num_signals_notified(0)
        client.metric.assert_called_once_with(type_=metric_type, labels={})
        client.resource.assert_called_once_with('global', labels={})
        return client, metric, resource

    def test_process_signals_default_config(self):
        """Each signal calls write_point"""
        signals = [Signal({'value': 3.14})]
        client, metric, resource = self._test(signals)
        client.write_point.assert_called_once_with(metric, resource, 3.14)

    def test_process_signals(self):
        """Each signal calls write_point"""
        config = {
            'value': '{{ $float }}',
            'metric_type': 'some_metric',
        }
        signals = [Signal({'float': 0.99})]
        client, metric, resource = self._test(signals, config)
        client.write_point.assert_called_once_with(metric, resource, 0.99)

    def test_process_signals_list(self):
        """Each signal calls write_point"""
        signals = [
            Signal({'value': 0.99}),
            Signal({'value': 3.14}),
        ]
        client, metric, resource = self._test(signals)
        self.assertEqual(client.write_point.call_count, 2)
        client.write_point.assert_any_call(metric, resource, 0.99)
        client.write_point.assert_any_call(metric, resource, 3.14)
