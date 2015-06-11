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
client_list = {} # 'client name': 'client id'
client_list_payload = {'service': 'list_clients'}

site_list_payload = {'service': 'list_sites', 'clientid': '204379'}

class Client:
    """Client object to hold client_name, client_id, site_id, device_id(s) etc."""
   
    client_count = 0
    device_count = 0
    master_device_list = {} 

    def __init__(self, name, client_id):
        self.name = name
        self.client_id = client_id
        self.site_list = {}
        self.device_list = {}

        Client.client_count += 1

    def dispClient(self):
        print 'Client name: ', self.name
        'Client id: ', self.client_id

    def dispCount(self):
        print 'Total clients: %d' % Client.client_count

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
        Device.master_device_dict (dict) : Dictionary of device names and ids

    """
    master_device_dict = {}

    def __init__(self, name, id, client_id):
        """Initialize the Device object with basic information.

        Args:
            name : Device hostname/computer name
            id : Device ID number
            site_name : Associated site name
            site_id : Associated site ID number
            client_name : Associated client name
            client_id : Associated client ID number

        """
        self.name = name
        self.id = id
        self.site_name = ''
        self.site_id = ''
        self.client_name = ''
        self.client_id = client_id 
        self.threat_list = []

    def get_id(self):
       return self.id 

def dispSites():
    print '\n***Client name: ID***\n***\tSite name: ID***\n'
    for i in client_list:
        print i, ':', client_list[i].client_id
        for g in client_list[i].site_list:
            print '\t', g, ':', client_list[i].site_list[g]

def dispClients():
    print '\n***Client name: ID***\n'
    for i in client_list:
        print i, ':', client_list[i].client_id

def dispDevices():
    """Display gathered devices and deviceIDs"""
    for cur_client in client_list.values():
        print cur_client.name
        print 'Device name\tID'
        for target in cur_client.device_list:
            print cur_client.device_list[target].name, ':', cur_client.device_list[target].id

def get_id(cur_client, target):
    """Take client and device name, return Device ID"""
    if client_list[cur_client].device_list.has_key(target):
        return client_list[cur_client].device_list[target].id
    else:
        print ''
        print '%s was not found in %s device list' % (target.upper(), cur_client.capitalize())
        return ''

def put_data(result_1, result_2, id_type, cur_client=None, devicetype=None):
    """Add key:values taken from get(s) to Client instances.
       result_1 should be parent tag (i.e all_name)
       result_2 should be child tag (i.e. clientid or siteid)
    """
    for i in range(len(result_1)):
        tmp = unicode(result_1[i].string)
        val_1 = tmp[7:-2].lower()
        val_2 = unicode(result_2[i].string).lower()

        if id_type == 'clientid':
            client_list[val_1] = Client(val_1, val_2)
        
        elif id_type == 'siteid':
            cur_client.site_list[val_1] = val_2

        elif id_type == 'deviceid':
            tmp = unicode(result_1[i].contents[1].string)
            dev_name = tmp[7:-2].lower()
            dev_id = unicode(result_1[i].contents[0].string)
            client_id = cur_client.client_id 
            
            dev_inst = Device(dev_name, dev_id, client_id)
             
            cur_client.device_list[dev_inst.name] = dev_inst

            Device.master_device_dict[dev_name] = dev_inst

def extract_data(id_type, data=None, cur_client=None, devicetype=None, dev_id=None):
    """Filter and extract desired key:values from https GET resp and call
    put_data() to add attributes to instances
    """
    #This block is only for testing. 
    #Remove and confirm correct function with https GET before deploy
    #if data:
    if data == None:
        if id_type == 'clientid':
            filename = './data/tempFile'
            search_1 = 'name'
            search_2 = 'clientid'

        elif id_type == 'siteid':
            filename = './data/%s_siteData' % cur_client.client_id
            search_1 = 'name'
            search_2 = 'siteid'

        elif id_type == 'deviceid':
            filename = './data/devices/old/%s_%s_deviceData' % (cur_client.client_id, devicetype)
            search_1 = devicetype
            search_2 = 'id'
        
        elif id_type == 'mavscan':
            pass 

        with open(filename, 'r') as f:
            data = f.read() 
            f.close()
        
        soup = bsoup(data, 'html5lib')
         
    else: 
        soup = bsoup(data.text, 'html5lib')

    #soup = bsoup(data.text, 'html5lib')
    result_1 = soup.find_all(search_1)
    result_2 = soup.find_all(search_2)
    
    if len(result_1) != len(result_2):
        #print "\nNumber of client names and ids do not match"
        pass
    return result_1, result_2

def extract_scan_data(response_data, cur_client, dev_id, dev_name):
    """Return a structure containing threat data"""
   
    #This block is only for testing. 
    # Remove and confirm correct function of https GET before deploy
    filename = './data/scans/%s_%s_scandata' % (cur_client.name, dev_id)
    with open(filename, 'r') as f:
        response_data = f.read()
        f.close()

    soup = bsoup(response_data, 'html5lib')
    
    search_1 = 'threat'
    search_2 = 'trace'

    result_1 = soup.find_all(search_1)
   
    # Each device will receive one threat list containing a dictionary for each threat.
    # Each threat_dict contains the name, status, type etc. and a trace_list
    # Each trace_list contains the paths for each trace dealt with under that particular threat

    threat_list = []

    match_num = len(result_1)
    print '\n**************'
    print 'Looking at', dev_name
    print 'ID is', dev_id
    print 'Number of Threats found', match_num 
    
    for threat in result_1:
        
        threat_dict = {}
        trace_list = []
        threat_dict['dev_id'] = dev_id
        threat_dict['name'] = threat.contents[0].string
        threat_dict['status'] = threat.status.string
       
        result_2 = threat.find_all(search_2)
        
        t = 0
        for trace in result_2:
            trace_list.append(trace.description.string)
            t += 1

        # status FAILED_TO_QUARANTINE returns a threat.count of None
        if threat.count != None:
            threat_dict['count'] = threat.count.string
        else:
            threat_dict['count'] = t
        
        for sib in threat.parent.previous_siblings:
            if sib.name == 'start':
                threat_dict['start'] = sib.string 
            
            if sib.name == 'type':
                threat_dict['type'] = sib.string 
        
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

        threat_dict['traces'] = trace_list

        threat_list.append(threat_dict)

    return threat_list

def acquire_data(id_type, cur_client=None, devicetype=None, dev_id=None):
    """https GET response from server and call extract_data() in it"""
    if id_type == 'clientid':
        payload = {'service': 'list_clients'}
        
        #Uncomment and test https GET for deploy
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = None

    if id_type == 'siteid':
        payload = {'service': 'list_sites', 'clientid': cur_client.client_id}
        #Uncomment and test https GET for deploy
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = None

    if id_type == 'deviceid':
        payload = {'service': 'list_devices_at_client', 'clientid': cur_client.client_id, 'devicetype': devicetype}

        #Uncomment and test https GET for deploy
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = None 
    if id_type == 'mavscan':
        payload = {'service': 'list_mav_scans', 'deviceid': dev_id, 'details': 'YES'}
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = None
        
    return resp

def write_out_data():
    """For dev, write out data to use while testing"""

    with open('./data/devices/%s_%s_deviceData' % (cur_client.client_id, devicetype), 'w') as f:
        f.write(resp.text.encode('utf-8'))
        f.close()

def produce_scan_results(client_name=None):
    id_type = 'mavscan'
    
    cur_client = client_list[client_name]
    print 'Gather scan data for ', cur_client.name
    for cur_client in client_list.values():
        for dev_id in cur_client.device_list.values():
            response_data = acquire_data(id_type, cur_client=cur_client, dev_id=dev_id)

def get_device_threat_data(dev_name):
    dev_name = dev_name
    dev_id =  Device.master_device_dict[dev_name].id
    cur_client_id = Device.master_device_dict[dev_name].client_id
    threat_data = extract_scan_data(response_data, cur_client_id, dev_id, dev_name)

def main():

    # Stanza to generate clients
    id_type = 'clientid'
    response_data = acquire_data(id_type)
    data_1, data_2 = extract_data(id_type, response_data)
    put_data(data_1, data_2, id_type)
    
    print ''
    
    # Stanza to generate sites
    id_type = 'siteid'
    for cur_client in client_list.values():
        response_data = acquire_data(id_type, cur_client)
        data_1, data_2 = extract_data(id_type, response_data, cur_client)
        put_data(data_1, data_2, id_type, cur_client)
    
    # Stanza to generate devices
    id_type = 'deviceid'
    device_type_list = ['workstation', 'server']
    for device_type in device_type_list:
        for cur_client_id in client_list.values():
            response_data = acquire_data(id_type, cur_client_id, device_type)
            data_1, data_2 = extract_data(id_type, response_data, cur_client_id, device_type)
            put_data(data_1, data_2, id_type, cur_client_id, device_type)

    '''
    # Stanza to generate scandata
    id_type = 'mavscan'
    for cur_client in client_list.values():
        for cur_device in cur_client.device_list.values():
            dev_name = cur_device.name
            dev_id = cur_device.id
            response_data = acquire_data(id_type, cur_client=cur_client, dev_id=dev_id)
            threat_data = extract_scan_data(response_data, cur_client=cur_client, dev_id=dev_id, dev_name=dev_name)
    cur_client = client_list['cherokee']
    dev_id = '1734074'
    dev_name = 'optiplex001'
    threat_data = extract_scan_data(response_data, cur_client=cur_client, dev_id=dev_id, dev_name=dev_name)
            print '\nData has been built and returned to main()'
            print ''
            threat_num = range(len(threat_data))
            if threat_num > 0:
                for i in range(len(threat_data)):
                    print 'threat name', threat_data[i]['name']
                    for j in range(len(threat_data[i]['traces'])):
                        print 'trace: ', threat_data[i]['traces'][j]
                #raw_input('Is the dict information displaying correctly?')

            print '\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
    '''
    #get_device_threat_data('optiplex001')
    #produce_scan_results('united imaging')

    #dispClients()
    #dispSites()
    dispDevices()

if __name__ == '__main__':
    main()
