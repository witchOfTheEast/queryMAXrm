#! /usr/bin/python2

# Python 2.7 script
from bs4 import BeautifulSoup as bsoup
import requests
from datetime import date
from calendar import monthrange
from lxml import etree
import disp
from classes import Client, Device
import response
import createpdf

# NOTE: If API key is regenerated in MAXrm it *must* be updated here
# NOTE: BeautifulSoup deals in unicode, python str may need .encode('utf-8')
# appended, esp. when piping or writing out to file

api_key = '6p3t2wsX2nOyUwjNAN5JXLHJRGzT3SGN'
query_server = 'www.systemmonitor.us'
    
def client_id_name(client):
    """Returna  tuple of ('client_name', client_id)""" # TODO This code is still broken
    try:
        client_id = Client.inst_by_name[client].id
        client_name = client
    except KeyError:
        # fallback to 'client' parameter is id
        try:
            client_name = Client.inst_by_id[int(client)].name
            client_id = client
        except KeyError:
            pass
        
    return (client_name, client_id)

def device_id_name(device):
    """Return a tuple of ('device name', device_id)""" # TODO This code is still broken
    try:
        device_id = Device.inst_by_name[device].id
        device_name = device
    except KeyError:
        # fallback to 'device' parameter is id
        try:
            device_name = Device.inst_by_id[int(device)].name
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

def get_response(data_type, client_id=None, device_id=None):
    """Request GET from API server based on desired type, return raw response data"""
    if data_type == 'client':
        payload = {'service': 'list_clients'}
        
        #Uncomment and test https GET for deploy
        temp_resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = temp_resp.text
        #resp = None
    
    if data_type == 'site':
        payload = {'service': 'list_sites', 'clientid': client_id}
        #Uncomment and test https GET for deploy
        temp_resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = temp_resp.text
        #resp = None

    if data_type == 'device':
        device_type = ('workstation', 'server')
        resp = ''
        for dev_type in device_type:
            payload = {'service': 'list_devices_at_client', 'clientid': client_id, 'devicetype': dev_type}
            #Uncomment and test https GET for deploy
            temp_resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
            resp += temp_resp.text
            #resp = None

    if data_type == 'scan':
        payload = {'service': 'list_mav_scans', 'deviceid': device_id, 'details': 'YES'}
        temp_resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = temp_resp.text
        #resp = None
        
    return resp

def gen_client_info():
    """Generate Client instances with info"""
    data_type = 'client'
    raw_response = get_response(data_type)
    parsed_data = response.parse(raw_response, data_type)
    create_client_inst(parsed_data)

def gen_site_info():
    """Generate Site info and put into Client instances"""
    data_type = 'site'
    for client_id in Client.inst_by_id.keys(): 
        raw_response = get_response(data_type, client_id)
        parsed_data = response.parse(raw_response, data_type, client_id)
        append_site_info(parsed_data, client_id)

def gen_device_info():
    """Generate Device info and put into Device instances"""
    data_type = 'device'
    for client_id in Client.inst_by_id.keys():
        raw_response = get_response(data_type, client_id)
        parsed_data = response.parse(raw_response, data_type, client_id)
        create_dev_inst(parsed_data, client_id)

def gen_scan_info_all():
    """Generate scan info for each device in Device.inst"""
    for device_id in Device.inst_by_id.keys():
        gen_device_scan_info(device_id)

def gen_device_scan_info(device):
    """Take either device name or id, get the threat_dict and append it to the Device instance"""
    data_type = 'scan'
   
    device_name, device_id = device_id_name(device)
    
    raw_response = get_response(data_type, device_id=device_id)
    parsed_data = response.parse_scan(raw_response, device_id, device_name)
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
    disp.device_names(Client.inst_by_name) 
    
    target = raw_input('\n>').lower()
    if target == 'quit':
        exit()
    else:
        print device_id_name(target)
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
    #print '\n*****************'
    #print 'Range:', date_range
    
    for device_id in Client.inst_by_id[client_id].device_id_dict.keys():
        device_name = device_id_name(device_id)[0]
        dev_threat_list = scan_from_range(device_id, date_range)
        client_threat_dict[device_name] = dev_threat_list
  
    return client_threat_dict

def gen_month_report_doc(client, year, month):
    """Write text file to to be used in .pdf production"""
    client_threat_dict = month_report(client, year, month)
    client_name = client # client name text
    
    root = etree.Element('root')
     
    #root.append( etree.Element('client_name') )
    tag_client_name = etree.SubElement(root, 'client_name')
    tag_client_name.text = client_name
        
    for threat_list in client_threat_dict.values():
        #print 'device name', threat_list[0]
        #print 'number of threats', len(threat_list[1:])
        if len(threat_list) > 1:
            for threat in threat_list[1:]:
                #print 'threat name', threat['name']
                for trace in threat['traces']:
                    #print 'trace', trace
                    pass

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
    
    xml_string = etree.tostring(root, pretty_print=True)

    if month < 10:
        month_str = '0%s' % str(month)

    filename = '_'.join([client_name, str(year), month_str, 'threat_report'])
    out_file = './threat_reports/%s.pdf' % filename
    createpdf.build_pdf(out_file, xml_string) 
    
def all_clients_month_report(year, month):
    for client_name in Client.inst_by_name.keys():
       gen_month_report_doc(client_name, year, month)

def populate_database():
    """Call the functions to generate instances and populate them with data"""
    gen_client_info()
    gen_site_info()
    gen_device_info()
    #gen_scan_info_all()

def main():
    print '\nGathering information and building data structures.\nThis will take a moment....'
    populate_database()
    
    #all_clients_month_report(2015, 6)

    #gen_month_report_doc('mosm', 2015, 05)
    
    #client_threat_dict = month_report('mosm', 2015, 05)
    
    #disp.client_threats(client_threat_dict, 'mosm')
    query_user()
    #disp.clients(Client.inst_by_name)
    #disp.sites(Client.inst_by_id)
    #disp.devices_all(Device.inst_by_name)
    #disp.device_names(Client.inst_by_name)

if __name__ == '__main__':
    main()
