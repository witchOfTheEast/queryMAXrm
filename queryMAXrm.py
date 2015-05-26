#! /usr/bin/python2

# Python 2.7 script
# 
# Gather desired information from MAXrm 
#
# Requires requests, BeautifulSoup from bs4
#
# NOTE: If API key is regenerated in MAXrm it *must* be updated here
# NOTE: BeautifulSoup deal in unicode, python str may need .encode('utf-8')
# appended, esp. when piping or writing out to file
import requests
from bs4 import BeautifulSoup as bsoup

# Global variables
api_key = '6p3t2wsX2nOyUwjNAN5JXLHJRGzT3SGN'
query_server = 'www.systemmonitor.us'
client_list = {}
client_list_payload = {'service': 'list_clients'}
# will the server take a list for the clientids
site_list_payload = {'service': 'list_sites', 'clientid': '204379'}

class Client:
    """Client object to hold client_name, client_id, site_id, device_id(s) etc."""
   
    client_count = 0
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

def put_data(result_1, result_2, type, cur_client=None):
    """Add key:values taken from get(s) to Client instances.
       result_1 should be parent tag (i.e all_name)
       result_2 should be child tag (i.e. clientid or siteid)
    """
    
    for i in range(len(result_1)):

        tmp = unicode(result_1[i].string)
        val_1 = tmp[7:-2]
        
        val_2 = unicode(result_2[i].string)

        if type == 'clientid':
            client_list[val_1] = Client(val_1, val_2)
        
        elif type == 'siteid':
            cur_client.site_list[val_1] = val_2
    
def extract_data(type, data=None, cur_client=None):
    """Filter and extract desired key:values from https GET resp and call
    put_data() to add attributes to instances
    """
    #This block is only for testing. 
    #Removing and confirm correct function with https GET before deploy
    if data == None:
        if type == 'clientid':
            filename = './data/tempFile'
            search_1 = 'name'
            search_2 = 'clientid'

        elif type == 'siteid':
            filename = './data/%s_siteData' % cur_client.client_id
            search_1 = 'name'
            search_2 = 'siteid'

        with open(filename, 'r') as f:
            data = f.read() # data is either
            f.close()
        
        soup = bsoup(data, 'html5lib')
    
    else: 
        soup = bsoup(data.text, 'html5lib')

    result_1 = soup.find_all(search_1)
    result_2 = soup.find_all(search_2)
    
    if len(result_1) != len(result_2):
        print "\nNumber of client names and ids do not match"
    return result_1, result_2

def acquire_data(type, cur_client=None, devicetype=None):
    """https GET response from server and call extract_data() in it"""
    if type == 'clientid':
        payload = {'service': 'list_clients'}
        
        #Uncomment and test https GET for deploy
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = None

    if type == 'siteid':
        payload = {'service': 'list_sites', 'clientid': cur_client.client_id}
        #Uncomment and test https GET for deploy
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = None

    if type == 'deviceid':
        payload = {'service': 'list_devices_at_client', 'clientid': cur_client.client_id, 'devicetype': devicetype}

        #Uncomment and test https GET for deploy
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
    
        resp = None
        
    return resp

def write_out_data():
    """For dev, write out data to use while testing"""

    with open('./data/devices/%s_%s_deviceData' % (cur_client.client_id, devicetype), 'w') as f:
        f.write(resp.text.encode('utf-8'))
        f.close()

def main():

    # Stanza for client list
    type = 'clientid'
    response_data = acquire_data(type)
    data_1, data_2 = extract_data(type, response_data)
    put_data(data_1, data_2, type)
    #dispClients()
    
    print ''
    
    # Stanza for site list
    type = 'siteid'
    for cur_client in client_list.values():
        response_data = acquire_data(type, cur_client)
        data_1, data_2 = extract_data(type, response_data, cur_client)
        put_data(data_1, data_2, type, cur_client)
    #dispSites()
    
    type = 'deviceid'
    device_type_list = ['workstation', 'server']
    for device_type in device_type_list:
        for cur_client in client_list.values():
            response_data = acquire_data(type, cur_client, device_type)
            #data_1, data_2 = extract_data(type, response_data, cur_client)
            #put_data(data_1, data_2, type, cur_client)


if __name__ == '__main__':
    main()
