#! /usr/bin/python2

# Python 2.7 script
# 
# Gather desired information from MAXrm 
#
# Requires requests, BeautifulSoup from bs4
#
# NOTE: If API key is regenerated in MAXrm it *must* be updated here
# NOTE: BeautifulSoup deals in unicode, python str may need .encode('utf-8')
# appended, esp. when piping or writing out to file

import requests
from bs4 import BeautifulSoup as bsoup

# Global variables
api_key = '6p3t2wsX2nOyUwjNAN5JXLHJRGzT3SGN'
query_server = 'www.systemmonitor.us'

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

    def __init__(self, name, id):
        """Initilize Device instance with name and id.

        Args: 
            name (str) : Device name 
            id (int) : Device ID number
        """

        self.name = name
        self.id = id
        self.client_name = None
        self.client_id = None
        self.site_name = None
        self.site_id = None
        self.threat_list = []
        
        Device.inst_by_name[name] = self
        Device.inst_by_id[id] = self

def dispClients():
    """Iterate over Clients.inst_by_name and display client names and IDs"""
    print '\n***Client Name: Client ID***\n'
    for inst in Client.inst_by_name.values():
        print inst.name, ':', inst.id

def dispSites():
    """Iterate over site_name_dict for each Client.inst_by_name.value and
    display site names and IDs
    """
    
    for inst in Client.inst_by_name.values():
        print '\n***Client Name: Client ID***\n'
        print inst.name, ':', inst.id
        print '\n\t***Site Name: Site ID***\n'

        for key in inst.site_name_dict.keys():
            print '\t',key, ':', inst.site_name_dict[key]
        
        for id in inst.site_id_dict.keys():
            print '\t',inst.site_id_dict[id], ':', id 

def dispDevicesAll():
    """Iterate over Devices.inst_by_name and display device names and IDs"""
    print '\n***Device Name: Device ID***\n'
    for inst in Devices.inst_by_name.values():
        print inst.name, ':', inst.id

def create_dev_inst(input):
    """Create Device instance from response data"""
    pass

def create_client_inst(data):
    """Create Client instance from response data"""
    result_1 = data[0]
    result_2 = data[1]
    data_type = data[2]

    for i in range(len(result_1)):
        temp = unicode(result_1[i].string)
        value_1 = temp[7:-2].lower()
        value_2 = int(result_2[i].string)
    
        if data_type == 'client':
            name = value_1
            id = value_2
            inst = Client(name, id)
            Client.inst_by_name[name] = inst
            Client.inst_by_id[id] = inst 

def append_site_info(data, client_id):
    """Append site info from response data to client and device instances passed as parameters"""
    result_1 = data[0]
    result_2 = data[1]
    data_type = data[2]

    for i in range(len(result_1)):
        temp = unicode(result_1[i].string)
        value_1 = temp[7:-2].lower()
        value_2 = int(result_2[i].string)
    
        if data_type == 'site':
            name = value_1
            id = value_2
            inst = Client.inst_by_id[client_id]
            inst.site_name_dict[name] = id
            inst.site_id_dict[id] = name 

def parse_response(data, data_type, client_id=None):
    """Accept raw response, pull out desired data and return parsed response data"""
    # 'filename' is to skip GETs to server for faster testing
    if data_type == 'client':
        filename = './data/tempFile'
        search_1 = 'name'
        search_2 = 'clientid'

    elif data_type == 'site':
        filename = './data/%s_siteData' % client_id 
        search_1 = 'name'
        search_2 = 'siteid'

    elif data_type == 'device':
        filename = './data/devices/%s_%s_deviceData' % (cur_client.client_id, devicetype)
        search_1 = devicetype
        search_2 = 'id'
    
    elif data_type == 'mavscan':
        pass 
    
    # This block makes use of 'filename' for faster testing
    if data == None:
         with open(filename, 'r') as f:
            data = f.read() 
            f.close()
         soup = bsoup(data, 'html5lib')
         
    else: 
        soup = bsoup(data.text, 'html5lib')
    # If the above block relating to 'filename' is removed, this following line
    # must be uncommented and functionality tested
    #soup = bsoup(data.text, 'html5lib')
    result_1 = soup.find_all(search_1)
    result_2 = soup.find_all(search_2)
    
    if len(result_1) != len(result_2):
        print "\nNumber of client names and ids do not match"
        pass

    return (result_1, result_2, data_type)

def parse_scan_response(input):
    """Accept raw response, pull out desired threat data and return parsed response data"""
    pass
    
def get_response(data_type, client_id=None):
    """Request GET from API server based on desired type, return raw response data"""
    if data_type == 'client':
        payload = {'service': 'list_clients'}
        
        #Uncomment and test https GET for deploy
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = None
    
    if data_type == 'site':
        payload = {'service': 'list_sites', 'clientid': client_id}
        #Uncomment and test https GET for deploy
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = None

    if data_type == 'deviceid':
        payload = {'service': 'list_devices_at_client', 'clientid': cur_client.client_id, 'devicetype': devicetype}

        #Uncomment and test https GET for deploy
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = None 
    if data_type == 'mavscan':
        payload = {'service': 'list_mav_scans', 'deviceid': dev_id, 'details': 'YES'}
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = None
        
    return resp

def gen_client_info():
    """Generate Client instances with info"""
    data_type = 'client'
    raw_response = get_response(data_type)
    parsed_data = parse_response(raw_response, data_type)
    create_client_inst(parsed_data)

def gen_site_info():
    """Generate Site info and put into Client instances"""
    data_type = 'site'
    for client_id in Client.inst_by_id.keys(): 
        raw_response = get_response(data_type, client_id)
        parsed_data = parse_response(raw_response, data_type, client_id)
        append_site_info(parsed_data, client_id)

def main():
    """Call the functions to generate instances and populate them with data"""
   
    gen_client_info()

    gen_site_info()
    
    
    
    dispSites()

if __name__ == '__main__':
    main()

