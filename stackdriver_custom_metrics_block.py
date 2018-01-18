from google.cloud import monitoring
from nio.block.base import Block
from nio.properties import VersionProperty, FloatProperty, StringProperty


class StackdriverCustomMetrics(Block):

    version = VersionProperty('0.1.0')
    value = FloatProperty(title='Value', default='{{ $value }}')
    metric_type = StringProperty(
        title='Metric Type', default='custom.googleapis.com/metric')

    def process_signals(self, signals):
        client = monitoring.Client()
        metric = client.metric(type_=self.metric_type(), labels={})
        resource = client.resource('global', labels={})
        for signal in signals:
            client.write_point(metric, resource, self.value(signal))
