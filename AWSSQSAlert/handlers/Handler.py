import logging

class Handler(object):
    """
    Handlers process queue messages into actionable alerts.
    """
    def __init__(self):
        """
        Create a new instance of the Handler class
        """
        self.events = []
        self.logger = logging.getLogger('autoscale-alert') 
        
    def watches(self, event):
        """
        Returns true or false for whether than handler operates on that metric
        """
        raise Exception('Not Implemented')

    def alert(self, config, event, msg):
        """
        Processes an event into an alert
        """
        raise Exception('Not Implemented')