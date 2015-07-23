#Python 2.7
"""Provide Client and Device classes for queryMAXrm.py"""
class Client:
    """Client object to hold data.

    Attributes:
        name (str) : Client name
        id (int) : Client ID number
        site_name_dict (dict) : {'site name': 'site id'}
        site_id_dict (dict) : {'site id': 'site name'}
        device_name_dict (dict) : {'device name': device instance}
        device_id_dict (dict) : {'device id': device instance}
        
        Client.client_count : Number of client instances
        Client.inst_by_name (dict) : {'client name': 'client id'}
        Client.inst_by_id (dict) : {'client id': 'client name'}
    """
    
    client_count = 0
    inst_by_name = {}
    inst_by_id = {}

    def __init__(self, name, id):
        """Initialize Client instance with name and id.

        Args:
            name (str) : Client name 
            id (int) : Client ID 
        """
        self.name = name
        self.id = id
        self.site_name_dict = {}
        self.site_id_dict = {}
        self.device_name_dict = {}
        self.device_id_dict = {}

        Client.client_count += 1

        Client.inst_by_name[name] = self
        Client.inst_by_id[id] = self

class Device():
    """Device object with associated attributes.

    Attributes:
        name : Device hostname/computer name
        id : Device ID number
        site_name : Associated site name
        site_id : Associated site ID number
        client_name : Associated client name
        client_id : Associated client ID number
        threat_list (list) : List of dictionaries, 1 per threat
        
        Device.device_count (int) : Number of device instances
        Device.inst_by_name (dict) : {'device name': device instance}
        Device.inst_by_id (dict) : {'device id': device instance}
    """
    
    device_count = 0
    inst_by_name = {}
    inst_by_id = {}

    def __init__(self, name, id, client_id):
        """Initilize Device instance with name and id.

        Args: 
            name (str) : Device name 
            id (int) : Device ID number
            client_id : Associated client ID number
        """

        self.name = name
        self.id = id
        self.client_id = client_id
        self.site_name = None
        self.site_id = None
        self.threat_list = []
       
        client_name = Client.inst_by_id[client_id].name
        self.client_name = client_name
        
        Device.inst_by_name[name] = self
        Device.inst_by_id[id] = self
       
        Client.inst_by_id[client_id].device_name_dict[name] = self
        Client.inst_by_id[client_id].device_id_dict[id] = self
