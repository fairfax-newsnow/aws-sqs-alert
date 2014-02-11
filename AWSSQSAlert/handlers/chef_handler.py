from Handler import Handler
import boto.ec2
from pprint import pprint
from chef import autoconfigure, Node, Client, Search
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
        api = autoconfigure()

        instance_id = None
        hostname = None
        
        reservations = ec2.get_all_instances(instance_ids=[msg['EC2InstanceId']])
        self.logger.debug('chef_handler - Getting Instance information from EC2: %s'%msg['EC2InstanceId'] , extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name))
        
        found = False
        
        for r in reservations:
            for i in r.instances:
                
                self.logger.debug('chef_handler - Found Instance', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, hostname=hostname))

                if i.id == msg['EC2InstanceId']:
                    
                    found = True
                    
                    if len(i.private_dns_name) > 0:

                        hostname = i.private_dns_name[0:i.private_dns_name.index('.')]
                        
                        self.logger.debug('chef_handler - Checking Chef Server For hostname: %s'%hostname , extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, hostname=hostname))
                        
                        if hostname is not None:
                            node = Node(hostname)
                            client = Client(hostname, api=api)
                                                        
                        if node is not None:
                            try:
                                self.logger.debug('chef_handler - Found Node, Deleteing.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, hostname=hostname, action="node-delete"))
                                node.delete()
                                self.logger.info('chef_handler - Deleted Node.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, hostname=hostname, action="node-delete"))
                            except ChefServerNotFoundError as e:
                                self.logger.error('chef_handler - Failure Deleting Node.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, hostname=hostname, action="node-delete"))
                                pass
                            
                        if client is not None:
                            try:
                                self.logger.debug('chef_handler - Found Client, Deleteing.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, hostname=hostname, action="client-delete"))
                                client.delete()
                                self.logger.info('chef_handler - Deleted Client.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, hostname=hostname, action="client-delete"))
                            except ChefServerNotFoundError as e:
                                self.logger.error('chef_handler - Failure Deleting Client.', extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name, hostname=hostname, action="client-delete"))
                                raise
                            
        if found == False:
            self.logger.info('chef_handler - Could not find Instance information in EC2: %s'%msg['EC2InstanceId'] , extra=dict(program="autoscale-alert", handler="chef_handler", instance_id=msg['EC2InstanceId'], region=region.name))
