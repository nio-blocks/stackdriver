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
        default_filename = '[[PROJECT_ROOT]]/project-abcd1234.json'
        filename = config.get('service_account_file', default_filename)
        with patch(block.__module__ + '.monitoring') as monitoring:
            with patch(block.__module__ + '.service_account') as sa:
                client = MagicMock()
                metric = MagicMock()
                client.metric.return_value = metric
                resource = MagicMock()
                client.resource.return_value = resource
                monitoring.Client.from_service_account_json.return_value = \
                    client
                self.configure_block(block, config)
                block.start()
                block.process_signals(signals)
                block.stop()
        self.assert_num_signals_notified(0)
        monitoring.Client.from_service_account_json.assert_called_once_with(
            json_credentials_path=filename)
        client.metric.assert_called_once_with(type_=metric_type, labels={
            # Specify this label shouldn't be required but it seems to help.
            # For some reason, the resource type is not being set to 'global'
            # reliably without it.
            'resource_type': 'global',
        })
        client.resource.assert_called_once_with('global', labels={})
        return client, metric, resource

    def test_default_config(self):
        """Write one data point with default config"""
        signals = [Signal({'value': 3.14})]
        client, metric, resource = self._test(signals)
        client.write_point.assert_called_once_with(metric, resource, 3.14)

    def test_service_account_file_config(self):
        """Service Account File location is configurable"""
        config = {
            'service_account_file': 'file_location.json',
        }
        signals = [Signal({'value': 0.99})]
        client, metric, resource = self._test(signals, config)

    def test_value_and_metric_type_config(self):
        """Metric Type and value propety are configurable"""
        config = {
            'value': '{{ $float }}',
            'metric_type': 'some_metric',
        }
        signals = [Signal({'float': 0.99})]
        client, metric, resource = self._test(signals, config)
        client.write_point.assert_called_once_with(metric, resource, 0.99)

    def test_signal_list(self):
        """Write a data point for each signal"""
        signals = [
            Signal({'value': 0.99}),
            Signal({'value': 3.14}),
        ]
        client, metric, resource = self._test(signals)
        self.assertEqual(client.write_point.call_count, 2)
        client.write_point.assert_any_call(metric, resource, 0.99)
        client.write_point.assert_any_call(metric, resource, 3.14)
