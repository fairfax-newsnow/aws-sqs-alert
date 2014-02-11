aws-sqs-alert
===========

Alerting mechanism for AWS SQS Queues

Multiple handlers for targeting different messages.

Design for performing actions based on AutoScale messages sent to an SNS queue that then forward to an SQS queue.

Can also be used to consume CloudWatch Alerts, delete Chef Nodes/Clients on terminate and update statsD metrics.
