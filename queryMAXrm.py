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
from datetime import date
from calendar import monthrange
from lxml import etree
import disp

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
    
def disp_threats(threat_list):
    """Display the threat_dict data is a resonable way
    
        Args:
            threat_list (list) : Minimum length is 1. Device name at index[0],
                followed by a dictionary for each threat, if any at index[1:].
    """
    print '\n***Threats for %s***' % threat_list[0]
    
    if len(threat_list) == 1:
        print 'No threats found on %s' % threat_list[0]

    else:
        for threat in threat_list[1:]:
            if threat['type']:
                print '\t%s\t%s\t%s\t%s\t%s' % (threat['name'], threat['category'], threat['type'], threat['status'], threat['start'])
            else:
                print '\t%s\t%s\t%s' % (threat['name'], threat['status'], threat['start'])
      
        print '\n***Traces***'
        for threat in threat_list[1:]:
            print '\t%s' % threat['name']
            for trace in threat['traces']:
                print '\t\t%s' % trace

def client_id_name(client):
    """Returna  tuple of ('client_name', client_id)"""
    try:
        client_id = Client.inst_by_name[client].id
        client_name = client
    except KeyError:
        pass # fallback to 'client' parameter is id
    try:
        client_name = Client.inst_by_id[client].name
        client_id = client
    except KeyError:
        pass
    
    return (client_name, client_id)

def device_id_name(device):
    """Return a tuple of ('device name', device_id)"""
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
    
    return (device_name, device_id)

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
        threat_dict['dev_name'] = device_name
        threat_dict['dev_id'] = device_id
        threat_dict['name'] = threat.contents[0].string
        threat_dict['status'] = threat.status.string
        threat_dict['category'] = threat.category.string 
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
    
def scan_from_range(device, date_range):
    """Return the threat_list for a device within a specified range
  
        Args:
            device : Either device name (str) or device id (int)
            date_range (list) : start date end date ['YYYY MM DD', 'YYYY MM DD']
    """
    
    # for testing
    #device = 'united-002'
    #date_range = ['2015 01 15', '2015 03 23']
    
    device_name = device_id_name(device)[0]
    device_id = device_id_name(device)[1]

    start_year = int(date_range[0][0:4])
    start_month = int(date_range[0][5:7])
    start_day = int(date_range[0][8:10])
    end_year = int(date_range[1][0:4])
    end_month = int(date_range[1][5:7])
    end_day = int(date_range[1][8:10])

    start_date = date(start_year, start_month, start_day)
    end_date = date(end_year, end_month, end_day)
 
    cur_dev_inst = Device.inst_by_id[device_id]
    cur_threat_list = cur_dev_inst.threat_list
    
    desired_threat_list = []
    desired_threat_list.append(device_name)
    for threat in cur_threat_list:
        date_str = threat['start']
        test_date = date(int(date_str[0:4]), int(date_str[5:7]), int(date_str[8:10]))
        
        if start_date < test_date < end_date:
            desired_threat_list.append(threat)
            
    return desired_threat_list

def query_user():
    disp.device_names() 
    
    target = raw_input('\n>').lower()
    if target == 'quit':
        exit()
    else:
        disp_device_scan(target)
    query_user()

def month_report(client_id, year, month):
    """Return a threat report for the provided client and the desired month"""
    client_id = client_id_name(client_id)[1]
    client_name = client_id_name(client_id)[0]
    first_day = 01
    last_day = monthrange(year, month)[1]
    client_threat_dict = {}

    date_range = ['%i %02i %02i' % (year, month, first_day), '%i %02i %02i' % (
        year, 
        month, 
        last_day
        )
        ]
    print '\n*****************8'
    print 'Range:', date_range
    
    for device_id in Client.inst_by_id[client_id].device_id_dict.keys():
        device_name = device_id_name(device_id)[0]
        dev_threat_list = scan_from_range(device_id, date_range)
        client_threat_dict[device_name] = dev_threat_list
  
    return client_threat_dict

def disp_client_threats(client_threat_dict, client_id):
    """Take a client_threat_dict and display threat information
    
        Args:
            client_threat_dict (dict) : Keys are device_names and values are threat_lists
    """
    client_name = client_id_name(client_id)[0]

    print 'Threats for client %s' % client_name
    for device in client_threat_dict.keys():
        disp_threats(client_threat_dict[device])

def gen_month_report_doc(client, year, month):
    """Write text file to to be used in .pdf production"""
    client_threat_dict = month_report(client, year, month)
    
    client_name = client # client name text
    
    root = etree.Element('root')
     
    #root.append( etree.Element('client_name') )
    tag_client_name = etree.SubElement(root, 'client_name')
    tag_client_name.text = client_name
        
    for threat_list in client_threat_dict.values():
        print 'device name', threat_list[0]
        print 'number of threats', len(threat_list[1:])
        if len(threat_list) > 1:
            for threat in threat_list[1:]:
                print 'threat name', threat['name']
                for trace in threat['traces']:
                    print 'trace', trace

        tag_device_name = etree.SubElement(tag_client_name, 'device_name')
        tag_device_name.text = threat_list[0]
        
        
        if len(threat_list) == 1:
            tag_threat = etree.SubElement(tag_device_name, 'threat')
            tag_threat_name = etree.SubElement(tag_threat, 'threat_name')
            tag_threat_name.text = 'No threats found'
        
        elif len(threat_list) > 1:
            for threat in threat_list[1:]:

                tag_threat = etree.SubElement(tag_device_name, 'threat')
                tag_threat_name = etree.SubElement(tag_threat, 'threat_name')
                tag_threat_name.text = threat['name']
                
                tag_threat_status = etree.SubElement(tag_threat, 'status')
                tag_threat_status.text = threat['status']

                tag_threat_date = etree.SubElement(tag_threat, 'date')
                tag_threat_date.text = threat['start']
                
                for trace in threat['traces']:
                    tag_threat_trace = etree.SubElement(tag_threat, 'trace')
                    tag_threat_trace.text = trace
                
    # for testing
    print (etree.tostring(root, pretty_print=True))
    with open('./data/testXML.xml', 'w') as f:
        f.write(etree.tostring(root))
        f.close

def populate_database():
    """Call the functions to generate instances and populate them with data"""
    gen_client_info()
    gen_site_info()
    gen_device_info()
    #gen_scan_info_all()

def main():
    print '\nGathering information and building data structures.\nThis will take a moment....'
    populate_database()
    
    #gen_month_report_doc('mosm', 2015, 05)
    
    #client_threat_dict = month_report('mosm', 2015, 05)
    #disp_client_threats(client_threat_dict, 'mosm')
    #query_user()
    #disp.clients(Client)
    #disp.sites(Client)
    #disp.devices_all(Device)
    disp.device_names(Client, Device)

if __name__ == '__main__':
    main()
