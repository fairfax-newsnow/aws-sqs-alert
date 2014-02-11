aws-sqs-alert
===========

Alerting mechanism for AWS SQS Queues

Multiple handlers for targeting different messages.

Design for performing actions based on AutoScale messages sent to an SNS queue that then forward to an SQS queue.

Can also be used to consume CloudWatch Alerts, delete Chef Nodes/Clients on terminate and update statsD metrics.

# Stable Version
```bash
pip install aws-sqs-alert
```

# Development Version
```bash
pip install git+git://github.com/Jumpshot/aws-sqs-alert.git#egg=aws-sqs-alert
```

# PyPi
https://pypi.python.org/pypi/aws-sqs-alert/

-------------------------------------------------------------

# Sample Configuration
```json
{
	"region" : "us-east-1",
	"sleep" : 120,
	"delete" : false,
	"queue" : "queuename",
	"log" : "/var/log/autoscale-alert.log",
	"handler_location" : "",
	"log_level" : "INFO",
	"num_messages" : 10,
	"active_handlers" : [
		"chef_handler",
		"graphite_handler"
	],
	"handler_config" : {
		"chef_handler" : {
		},
		"graphite_handler" : {
			"statsd_host" : "statsd.domain.ext"
		}
	} 
}
```