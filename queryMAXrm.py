#! /usr/bin/python2

# Python 2.7 script
# 
# Gather desired information from MAXrm 
#
# Requires requests, BeautifulSoup from bs4
#
# NOTE: If API key is regenerated in MAXrm it *must* be updated here
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

    def __init__(self, name, client_id):
        self.name = name
        self.client_id = client_id
        self.site_list = {}
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

def xacquire(payload):
    """Make https get to server with api key using supplied payload parameter(s)"""
    resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
    return resp

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

    put_data(result_1, result_2, type=type, cur_client=cur_client)

def acquire_data(type):
    """https GET response from server and call extract_data() in it"""
    if type == 'clientid':
        payload = {'service': 'list_clients'}
        
        #Uncomment and test https GET for deploy
        #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = None
        extract_data(type, resp)

    if type == 'siteid':
        for cur_client in client_list.values():
            payload = {'service': 'list_sites', 'clientid': cur_client.client_id}
            #Uncomment and test https GET for deploy
            #resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
            resp = None
            extract_data(type, resp, cur_client=cur_client)
    
def xpopulate_client_list():
    """Populate a list with desired information from get(s) to server"""
    #Using tempFile for testing. Un-comment for deploy.
    #client_data = acquire(client_list_payload)
    with open('./data/tempFile', 'r') as f:
        client_data = f.read()
        f.close()

    soup = bsoup(client_data, 'html5lib')

    all_clientid = soup.find_all('clientid')
    all_name = soup.find_all('name')

    if len(all_name) != len(all_clientid):
        print "\nNumber of client names and ids do not match"
    
    put_data(all_name, all_clientid, 'clientid')

def xextract_sites(data, cur_client):
    """Extract desired data from raw http response and add to Client instance(s)"""
    # using static files for testing. uncomment and adjust for deploy
    #soup = bsoup(data.text, 'html5lib')
    with open('./data/%s_siteData' % cur_client.client_id, 'r') as f:
        data = f.read()
        f.close()

    soup = bsoup(data, 'html5lib')

    all_siteid = soup.find_all('siteid')
    all_name = soup.find_all('name')

    if len(all_name) != len(all_siteid):
        print "\nNumber of site names and ids do not match"
    
    put_data(all_name, all_siteid, type='siteid', cur_client=cur_client)

def xpopulate_site_list():
    """Populate list with desired information from get(s) to server"""
    for cur_client in client_list.values():
        temp_payload = {'service': 'list_sites', 'clientid': cur_client.client_id}
        # using static files for testing. uncomment and adjust for deploy
        #site_data = acquire(temp_payload)
        site_data = ''
        extract_sites(site_data, cur_client)

'''
for i in list of client_ids:
    acquire sites
    put sites into correct Client instance
        by site name, site id
'''
#populate_client_list()
#populate_site_list()

#extract_data('clientid', data=None)

#for cur_client in client_list.values():
#    extract_data('siteid', data=None, cur_client=cur_client)

acquire_data('clientid')
acquire_data('siteid')

dispClients()
print ''
dispSites()
#print client_list['MOSM'].name, client_list['MOSM'].client_id


