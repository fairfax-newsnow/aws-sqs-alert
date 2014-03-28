aws-sqs-alert
===========

Alerting mechanism for AWS SQS Queues

Multiple handlers for targeting different messages.

Design for performing actions based on AutoScale messages sent to an SNS queue that then forward to an SQS queue.

Can also be used to consume CloudWatch Alerts, delete Chef Nodes/Clients on terminate and update statsD metrics.

This requires Python 2.7x due to something with my import strategy.

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

# Sample Configuration for /etc/aws-sqs-alert/config.json
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

```bash
sudo aws-sqs-alert --debug Production-MessageQueue-XXXXXXXXXX
```

Put your custom handlers in /etc/aws-sqs-alert/handlers/ and edit the config.

--------------------------------------------------------------------

### Chef Changes
```ruby
node.set['instance_id'] = %x[curl http://169.254.169.254/latest/meta-data/instance-id]
```
Make sure that all instances have an instance_id, you cannot tell IP or other unique information after the termination.

### Cloudformation Examples
Global Level of Templates
```json
{
    "AWSTemplateFormatVersion" : "2010-09-09",
    "Description" : "Global Scoping",
    "Parameters" : { },
    "Resources" : {

        "MessageQueue" : {
            "Type" : "AWS::SQS::Queue"
        },
        
        "MessageTopic" : {
            "Type" : "AWS::SNS::Topic",
            "Properties" : {
                "Subscription" : [
                    {
                        "Endpoint" : { "Fn::GetAtt" : ["MessageQueue", "Arn"]},
                        "Protocol" : "sqs"
                    }
                ]
            }
        },

        "SQSPolicy" : {
           "Type" : "AWS::SQS::QueuePolicy",
           "Properties" : {
              "PolicyDocument" : {
                 "Id" : "QueuePolicy",
                 "Statement" : [ {
                    "Sid":"Allow-SendMessage-To-Both-Queues-From-SNS-Topic",
                    "Effect":"Allow",           
                    "Principal" : {"AWS" : "*"},
                    "Action":["sqs:SendMessage"],
                    "Resource": "*",
                    "Condition": {
                        "ArnEquals": {
                            "aws:SourceArn": { "Ref" : "MessageTopic" }
                        }
                    }
                  } ]
              },
              "Queues" : [{ "Ref" : "MessageQueue" }]
           }
        }

    },

    "Outputs" : {
        
        "MessageTopic" : {
            "Value" : { "Ref" : "MessageTopic" },
            "Description" : "Topic for Message Bus"
        }

    }
    
}
```

AutoScale Level
```json
"ASGServerGroup" : {
	"Type" : "AWS::AutoScaling::AutoScalingGroup",
	"Properties" : {
	    "NotificationConfiguration" : {
	        "TopicARN" : { "Ref" : "MessageTopic" },
	        "NotificationTypes" : ["autoscaling:EC2_INSTANCE_LAUNCH", "autoscaling:EC2_INSTANCE_LAUNCH_ERROR", "autoscaling:EC2_INSTANCE_TERMINATE", "autoscaling:EC2_INSTANCE_TERMINATE_ERROR"]
	    }
	}
}
```