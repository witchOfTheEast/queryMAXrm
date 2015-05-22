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
    for i in client_list:
        print i, ':', client_list[i].client_id
        for g in client_list[i].site_list:
            print '\t', g, ':', client_list[i].site_list[g]

def dispClients():
    print 'Client name: ID'
    for i in client_list:
        print i, ':', client_list[i].client_id

def acquire(payload):
    """Make https get to server with api key using supplied payload parameter(s)"""
    resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
    return resp

def populate_client_list():
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

    for i in range(len(all_name)):

        client_name_tmp = unicode(all_name[i].string)
        client_name = client_name_tmp[7:-2]
        
        client_id = unicode(all_clientid[i].string)

        client_list[client_name] = Client(client_name, client_id)
    

def extract_sites(data, cur_client):
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

    for i in range(len(all_name)):

        site_name_tmp = unicode(all_name[i].string)
        site_name = site_name_tmp[7:-2]
        
        site_id = unicode(all_siteid[i].string)

        cur_client.site_list[site_name] = site_id
   
def populate_site_list():
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
populate_client_list()
populate_site_list()
dispClients()
print ''
dispSites()
#print client_list['MOSM'].name, client_list['MOSM'].client_id


