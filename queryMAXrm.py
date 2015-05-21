#! /usr/bin/python2

# Python 2.7 script
# 
# Gather desired information from MAXrm 
#
# Requires requests
#
# NOTE: If API key is regenerated in MAXrm it *must* be updated here
import requests
from bs4 import BeautifulSoup as bsoup

# Global variables
api_key = '6p3t2wsX2nOyUwjNAN5JXLHJRGzT3SGN'
query_server = 'www.systemmonitor.us'
client_id_list = {}

def acquire():

    resp = requests.get('https://%s/api/?apikey=%s&service=list_clients' % (query_server, api_key))
    return resp

#resp2 = requests.post('https://%s/api/?apikey=%s&service=list_clients' % (query_server, api_key)) 

# Using tempFile for testing. Un-comment for deploy.
# client_data = acquire()
with open('./tempFile', 'r') as f:
    client_data = f.read()
    f.close()

soup = bsoup(client_data, 'html5lib')

value = soup.find_all('client')

for item in value:
    client_name_temp = unicode(item.contents[0].string)
    client_name = client_name_temp[7:-2] 
     
    
    client_id = unicode(item.contents[1].string)
    client_id_list[client_name] = client_id

for i in client_id_list:
    print i, client_id_list[i]


