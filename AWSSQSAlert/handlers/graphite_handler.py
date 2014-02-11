from Handler import Handler
import boto.ec2
import statsd
from boto.ec2.autoscale import AutoScaleConnection
from pprint import pprint

class graphite_handler (Handler):
    """
    Handlers process queue messages into actionable alerts.
    """
    def __init__(self):
        """
        Create a new instance of the Handler class
        """
        Handler.__init__(self)
        self.events = ['autoscaling:EC2_INSTANCE_TERMINATE', 'autoscaling:EC2_INSTANCE_LAUNCH', 'autoscaling:EC2_INSTANCE_FAILURE']
    
    def watches(self, msgtype, event):
        """
        Returns true or false for whether than handler operates on that metric
        """
        if msgtype != 'Event':
            return False
        
        for e in self.events:
            if e == event:
                return True
        return False
            

    def alert(self, config, event, msg):
        """
        Processes an event into an alert
        """
        for r in boto.ec2.autoscale.regions():
            if r.name == config['region']:
                region = r
                break
        
        stats = statsd.StatsClient(config['handler_config']['graphite_handler']['statsd_host'])
        
        ec2 = boto.connect_autoscale(aws_access_key_id=config['AWS_ACCESS'], aws_secret_access_key=config['AWS_SECRET'], region=region)
        asg = ec2.get_all_groups(names=[msg['AutoScalingGroupName']])
        self.logger.debug('graphite_handler - Getting AutoScale information from EC2: %s'%msg['AutoScalingGroupName'] , extra=dict(program="autoscale-alert", handler="graphite_handler", auto_scale_group=msg['AutoScalingGroupName'], region=region.name))
        
        if len(asg) > 0:
            self.logger.debug('graphite_handler - Updating statsD Metrics for: %s'%msg['AutoScalingGroupName'] , extra=dict(program="autoscale-alert", handler="graphite_handler", auto_scale_group=msg['AutoScalingGroupName'], region=region.name))
            stats.gauge("amazon.ec2.autoscale.%s.desired_capacity"%msg['AutoScalingGroupName'], asg[0].desired_capacity)
            stats.gauge("amazon.ec2.autoscale.%s.min"%msg['AutoScalingGroupName'], asg[0].min_size)
            stats.gauge("amazon.ec2.autoscale.%s.max"%msg['AutoScalingGroupName'], asg[0].max_size)
            self.logger.info('graphite_handler - Updated statsD Metrics for: %s'%msg['AutoScalingGroupName'] , extra=dict(program="autoscale-alert", handler="graphite_handler", auto_scale_group=msg['AutoScalingGroupName'], region=region.name))
        else:
            self.logger.info('graphite_handler - Could not find AutoScale Information from EC2: %s'%msg['AutoScalingGroupName'] , extra=dict(program="autoscale-alert", handler="graphite_handler", auto_scale_group=msg['AutoScalingGroupName'], region=region.name))