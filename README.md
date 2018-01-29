StackdriverCustomMetrics
========================
Write custom metrics to Google Stackdriver. https://cloud.google.com/monitoring/custom-metrics/creating-metrics#monitoring-write-timeseries-protocol

Properties
----------
- **metric_type**: The metric type to write the value to. Custom metrics must begin with `custom.googleapis.com/`. If the metric type does not exist yet, it will be created in the Global resource.
- **service_account_file**: To authenticate with the Google Stackdriver project, generate a service account private key. Download the json file and configure this property to the location of it. https://cloud.google.com/storage/docs/authentication#generating-a-private-key
- **value**: The floating point value to write to Stackdriver.

Inputs
------
- **default**: Signals that contain the value to write to Stackdriver.

Outputs
-------
None

Commands
--------
None

