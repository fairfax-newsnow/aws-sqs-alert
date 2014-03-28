from Handler import Handler
import boto.ec2
from pprint import pprint

import chef
from chef.exceptions import ChefServerNotFoundError

class chef_handler (Handler):
    """
    Handlers process queue messages into actionable alerts.
    """
    def __init__(self):
        """
        Create a new instance of the Handler class
        """
        Handler.__init__(self)
        self.events = ['autoscaling:EC2_INSTANCE_TERMINATE']

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
            

    def alert(self, config, msgtype, msg):
        """
        Processes an event into an alert
        """
        for r in boto.ec2.regions():
            if r.name == config['region']:
                region = r
                break
        
        ec2 = boto.connect_ec2(aws_access_key_id=config['AWS_ACCESS'], aws_secret_access_key=config['AWS_SECRET'], region=region)
        api = chef.autoconfigure()

        instance_id = None
        client = None
        node = None
                
        self.logger.debug('chef_handler - Checking Chef Server For node matching: %s'%msg['EC2InstanceId'] , extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name))
        
        chefapiobject = chef.ChefAPI.from_config_file('/etc/chef/client.rb')
        nodes = chef.Search('node', 'instance_id:%s'%msg['EC2InstanceId'], api=chefapiobject)
        
        if nodes is not None:
            for n in nodes:
                try:
                    node = chef.Node(n["name"])
                except:
                    pass
                
                try:
                    client = chef.Client(n["name"])
                except:
                    pass
                
                break
            
        if node is not None:
            try:
                self.logger.debug('chef_handler - Found Node, Deleting.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, action="node-delete"))
                node.delete()
                self.logger.info('chef_handler - Deleted Node.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, action="node-delete"))
            except ChefServerNotFoundError as e:
                self.logger.error('chef_handler - Failure Deleting Node.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, action="node-delete"))
                pass
            
        if client is not None:
            try:
                self.logger.debug('chef_handler - Found Client, Deleting.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, action="client-delete"))
                client.delete()
                self.logger.info('chef_handler - Deleted Client.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, action="client-delete"))
            except ChefServerNotFoundError as e:
                self.logger.error('chef_handler - Failure Deleting Client.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, action="client-delete"))
                raise
