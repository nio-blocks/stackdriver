from google.cloud import monitoring
from google.oauth2 import service_account
from nio import TerminatorBlock
from nio.properties import VersionProperty, FloatProperty, StringProperty


class StackdriverCustomMetrics(TerminatorBlock):

    version = VersionProperty('0.1.0')
    value = FloatProperty(title='Value', default='{{ $value }}')
    metric_type = StringProperty(
        title='Metric Type', default='custom.googleapis.com/metric')
    service_account_file = StringProperty(
        title='Service Account File',
        default='[[PROJECT_ROOT]]/project-abcd1234.json',
    )

    def process_signals(self, signals):
        client = monitoring.Client.from_service_account_json(
            json_credentials_path=self.service_account_file())
        metric = client.metric(type_=self.metric_type(), labels={
            'resource_type': 'global',
        })
        resource = client.resource('global', labels={})
        for signal in signals:
            self.logger.debug('Write {} to {}'.format(
                self.value(signal), self.metric_type()))
            client.write_point(metric, resource, self.value(signal))
