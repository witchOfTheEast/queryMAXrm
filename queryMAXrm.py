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
client_list = {}
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

    """
    def __init__(self, name, id):
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
        self.client_id = ''
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
            print cur_client.device_list[target].name, cur_client.device_list[target].id
            print ''

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
           
            dev_name = Device(dev_name, dev_id)
            
            cur_client.device_list[dev_name.name] = dev_name 

            Client.master_device_list[dev_name.name] = dev_name
            Client.device_count += 1
    
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
            filename = './data/devices/%s_%s_deviceData' % (cur_client.client_id, devicetype)
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
    
    temp_threat_list = []
    match_num = len(result_1)

    print 'Looking at', dev_name
    print 'id is', dev_id
    print 'Threats found', match_num 
    
    for threat in result_1:
        temp_threat_list.append(threat.contents[0].string)
        print 'name', threat.contents[0].string
        print 'status', threat.status.string
        print 'count', threat.count.string
       
        # This works as well, but appending .traces is likely to be really unclear that is is really a find_all('traces').find_all(search_2)
        #result_2 = threat.traces.find_all(search_2)
        #for trace in result_2:
        #    print trace.description.string 
        
        result_2 = threat.find_all(search_2)
        trace_count = 1
        for trace in result_2:
            print '\nTrace #' + str(trace_count), trace.description.string
            trace_count += 1
        print '' 
    print temp_threat_list
    raw_input("****")


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
        
def main():

    # Stanza for client list
    id_type = 'clientid'
    response_data = acquire_data(id_type)
    data_1, data_2 = extract_data(id_type, response_data)
    put_data(data_1, data_2, id_type)
    #dispClients()
    
    print ''
    
    # Stanza for site list
    id_type = 'siteid'
    for cur_client in client_list.values():
        response_data = acquire_data(id_type, cur_client)
        data_1, data_2 = extract_data(id_type, response_data, cur_client)
        put_data(data_1, data_2, id_type, cur_client)
    #dispSites()
    
    id_type = 'deviceid'
    device_type_list = ['workstation', 'server']
    for device_type in device_type_list:
        for cur_client in client_list.values():
            response_data = acquire_data(id_type, cur_client, device_type)
            data_1, data_2 = extract_data(id_type, response_data, cur_client, device_type)
            put_data(data_1, data_2, id_type, cur_client, device_type)

    id_type = 'mavscan'
    for cur_client in client_list.values():
        for cur_device in cur_client.device_list.values():
            dev_name = cur_device.name
            dev_id = cur_device.id
            response_data = acquire_data(id_type, cur_client=cur_client, dev_id=dev_id)
            myData = extract_scan_data(response_data, cur_client=cur_client, dev_id=dev_id, dev_name=dev_name)
            

    #produce_scan_results('united imaging')

    #dispDevices()
    temp_list = ['imac008', 'imac020']
    for target in temp_list:
        print '\nDevice %s' % target.upper(), get_id('cherokee', target=target) 

if __name__ == '__main__':
    main()
