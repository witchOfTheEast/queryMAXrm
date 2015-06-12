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
        
def dispDevicesAll():
    """Iterate over Devices.inst_by_name and display device names and IDs"""
    print '\n***Device Name: Device ID***\n'
    for inst in Device.inst_by_name.values():
        print inst.name, ':', inst.id

def disp_device_names():
    """Display device names in three columns"""
    client_dict = {}
    #for inst in Device.inst_by_name.values():
    #    name_list.append(inst.name)
    
    for client_inst in Client.inst_by_name.values():
        client_name = client_inst.name
        name_list = []
        for device_name in client_inst.device_name_dict.keys():
            name_list.append(device_name)
        
        client_dict[client_name] = name_list

    for client_name in client_dict.keys():
        name_rows = []
        name_list = client_dict[client_name]
        print '\n***%s %s devices***' % (client_name, len(name_list))

        i = 0
        while i < len(name_list):
            name_rows.append(name_list[i:i+6])
            i += 6  
     
        col_width = max(len(device_name) for row in name_rows for device_name in row) + 1 # padding
        for row in name_rows:
            print ''.join(word.ljust(col_width) for word in row)

def disp_device_scan(device):
    """Display the threat_dict data is a resonable way"""
    
    try:
        device_id = Device.inst_by_name[device].id
        device_name = device
    except KeyError:
        pass # fallback to 'device' parameter is id
    try:
        device_name = Device.inst_by_id[device].name
        device_id = device
    except KeyError:
        pass

    cur_list = Device.inst_by_id[device_id].threat_list
    
    print '\n***%s shows %s threats***' % (device_name, len(cur_list))
    print '\n***Threats***'
    
    for threat in cur_list:
        print '\t%s\t%s\t%s' % (threat['name'], threat['status'], threat['start'])
  
    print '\n***Traces***'
    for threat in cur_list:
        print '\t%s' % threat['name']
        for trace in threat['traces']:
            print '\t\t%s' % trace

    raw_input('\nPress any key to continue')

def create_dev_inst(data, client_id):
    """Create Device instance from response data"""
    result_1 = data[0]
    result_2 = data[1]
    data_type = data[2]
    
    for i in range(len(result_1)):
        temp = unicode(result_1[i].contents[1].string)
        dev_name = temp[7:-2].lower()
        dev_id = int(result_1[i].contents[0].string)
        
        Device(dev_name, dev_id, client_id)        

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
            Client(name, id)
            #Client.inst_by_name[name] = inst
            #Client.inst_by_id[id] = inst 

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
    # 'filename' can be used to skip GETs to server for faster testing
    if data_type == 'client':
        filename = './data/tempFile'
        search_1 = 'name'
        search_2 = 'clientid'

    elif data_type == 'site':
        filename = './data/%s_siteData' % client_id 
        search_1 = 'name'
        search_2 = 'siteid'

    elif data_type == 'device':
        filename = './data/devices/%s_devicedata' % client_id
        search_1 = ['workstation', 'server'] 
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
        soup = bsoup(data, 'html5lib')
    # If the above block opening 'filename' is removed, this following line
    # must be uncommented and functionality tested
    #soup = bsoup(data.text, 'html5lib')
    result_1 = soup.find_all(search_1)
    result_2 = soup.find_all(search_2)
    
    if len(result_1) != len(result_2):
        pass 
    
    return (result_1, result_2, data_type)

def parse_scan_response(data, device_id):
    """Accept raw response, pull out desired threat data and return parsed response data"""

    device_name = Device.inst_by_id[device_id].name

    #This block is only for testing. 
    # Remove and confirm correct function of https GET before deploy
    if data == None:
        filename = './data/scans/%s_scandata' % (device_id)
        with open(filename, 'r') as f:
            response_data = f.read()
            f.close()

        soup = bsoup(response_data, 'html5lib')
    
    else:
        soup = bsoup(data.text, 'html5lib')

    search_1 = 'threat'
    search_2 = 'trace'

    result_1 = soup.find_all(search_1)
   
    # Each device will receive one threat list containing a dictionary for each threat.
    # Each threat_dict contains the name, status, type etc. and a trace_list
    # Each trace_list contains the paths for each trace dealt with under that particular threat

    threat_list = []

    match_num = len(result_1)
    
    for threat in result_1:
        
        threat_dict = {}
        trace_list = []
        threat_dict['dev_id'] = device_id
        threat_dict['name'] = threat.contents[0].string
        threat_dict['status'] = threat.status.string
       
        result_2 = threat.find_all(search_2)
        
        t = 0
        for trace in result_2:
            trace_list.append(trace.description.string)
            t += 1

        # status FAILED_TO_QUARANTINE returns a threat.count of NoneType
        if threat.count != None:
            threat_dict['count'] = threat.count.string
        else:
            threat_dict['count'] = t
        
        for sib in threat.parent.previous_siblings:
            if sib.name == 'start':
                threat_dict['start'] = sib.string 
            
            if sib.name == 'type':
                threat_dict['type'] = sib.string 
        '''        
        print ''
        print 'name', threat_dict['name']
        print 'type', threat_dict['type']
        print 'status', threat_dict['status'] 
        print 'start', threat_dict['start']
        print 'Number of traces', threat_dict['count'] 
        print '\ntraces found'
        for i in range(len(trace_list)):
            count = i + 1
            print 'trace', count, trace_list[i]
        print ''
        '''
        threat_dict['traces'] = trace_list

        threat_list.append(threat_dict)

    return threat_list

def get_response(data_type, client_id=None, device_id=None):
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

    if data_type == 'device':
        device_type = ('workstation', 'server')
        resp = ''
        for dev_type in device_type:
            payload = {'service': 'list_devices_at_client', 'clientid': client_id, 'devicetype': dev_type}
            #Uncomment and test https GET for deploy
            #temp_resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
            #resp += temp_resp.text

            resp = None

    if data_type == 'scan':
        payload = {'service': 'list_mav_scans', 'deviceid': device_id, 'details': 'YES'}
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

def gen_device_info():
    """Generate Device info and put into Device instances"""
    data_type = 'device'
    for client_id in Client.inst_by_id.keys():
        raw_response = get_response(data_type, client_id)
        parsed_data = parse_response(raw_response, data_type, client_id)
        create_dev_inst(parsed_data, client_id)

def gen_scan_info_all():
    """Generate scan info for each device in Device.inst"""
    for device_id in Device.inst_by_id.keys():
        gen_device_scan_info(device_id)

def gen_device_scan_info(device):
    """Take either device name or id, get the threat_dict and append it to the Device instance"""
    data_type = 'scan'
    
    try:
        device_id = Device.inst_by_name[device].id
        device_name = device
    except KeyError:
        pass # fallback to 'device' parameter is id
    try:
        device_name = Device.inst_by_id[device].name
        device_id = device
    except KeyError:
        pass

    raw_response = get_response(data_type, device_id=device_id)
    parsed_data = parse_scan_response(raw_response, device_id)
    Device.inst_by_id[device_id].threat_list = parsed_data
    
def populate_database():
    """Call the functions to generate instances and populate them with data"""
    gen_client_info()
    gen_site_info()
    gen_device_info()
#    gen_scan_info_all()

def query_user():
    disp_device_names() 
    
    target = raw_input('\n>').lower()
    if target == 'quit':
        exit()
    else:
        disp_device_scan(target)
    query_user()

def main():
    print '\nGathering information and building data structures.\nThis will take a moment....'
    populate_database()
    
    query_user()
#    dispClients()    
#    raw_input('')
#    dispSites()
#    raw_input('')
#    dispDevicesAll()

if __name__ == '__main__':
    main()

