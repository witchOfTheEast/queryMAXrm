# Python 2.7 script
# Created by: Randall Dunn
# Email: justThisGuyRandall@gmail.com
# 2015/07/16

# customize the look of the .pdfs in createpdf.py

from bs4 import BeautifulSoup as bsoup
from datetime import date
from calendar import monthrange
from lxml import etree
import requests, os, ConfigParser, getopt, sys

# Custom modules
from classes import Client, Device
import response
import createpdf
import disp

def getConf():
    """Extract API key and server address from config.ini and return
    them in a dict {'api_key': KEY, 'query_server': SERVER}"""
    cwd = os.path.dirname(os.path.abspath(__file__))
    conf_file = os.path.join(cwd, '..', 'config.ini')

    if not os.path.isfile(conf_file):
        print 'Cannot locate %s' % conf_file

    opt_dict = {}

    config = ConfigParser.SafeConfigParser()

    config.read(conf_file)

    sections = config.sections()

    for section in sections:
        options  = config.options(section)
        
        for option in options:
            opt_dict[option] = config.get(section, option)
        
    return opt_dict   

def client_id_name(client):
    """Return a  tuple of ('client_name', client_id)
    
        Args:
            client: Either client name (str) or client id (int)
    """ 
    try: 
        client_id = int(client)
    except ValueError:
        if client in Client.inst_by_name:
            client_name = client
            client_id = Client.inst_by_name[client].id
        else:
            client_name, client_id = 'Not', 'found'
    else:
        if client in Client.inst_by_id:
            client_name = Client.inst_by_id[client].name
            client_id = client
        else:
            client_name, client_id = 'Not', 'found'
    
    return (client_name, client_id)

def device_id_name(device):
    """Return a tuple of ('device name', device_id)
        
        Args:
            device: Either device name (str) or device id (int)
    """ 
    try: 
        device_id = int(device)
    except ValueError:
        if device in Device.inst_by_name:
            device_name = device
            device_id = Device.inst_by_name[device].id
        else:
            device_name, device_id = 'Not', 'found'
    else:
        if device in Device.inst_by_id:
            device_name = Device.inst_by_id[int(device)].name
        else:
            device_name, device_id = 'Not', 'found'
    
    return (device_name, device_id)

def create_dev_inst(data, client_id):
    """Create Device instance from response data
        
        Args:
            data (tuple): Parsed response data
                (result_1, result_2, data_type)
            client_id (int): Active client ID number
    """
    result_1 = data[0]
    result_2 = data[1]
    data_type = data[2]
    
    for i in range(len(result_1)):
        temp = unicode(result_1[i].contents[1].string)
        dev_name = temp[7:-2].lower()
        dev_id = int(result_1[i].contents[0].string)
        
        Device(dev_name, dev_id, client_id)        

def create_client_inst(data):
    """Create Client instance from response data
        Args:
            data (tuple): Parsed response data
                (result_1, result_2, data_type)
    """
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

def append_site_info(data, client_id):
    """Set site related attributes to Client and Device instances

        Args:
            data (tuple): Parsed response data
                (result_1, result_2, data_type)
            client_id (int): Active client ID number
    """
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
    """Request GET from API server based on desired type, return
raw response data

        Args:
            data_type (str): Type of request, 'client', 'site',
                'device', 'scan'
            client_id (int): Active client ID number
            device_id (int): Active device ID number
    """
    if data_type == 'client':
        payload = {'service': 'list_clients'}
        
        temp_resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = temp_resp.text
    
    if data_type == 'site':
        payload = {'service': 'list_sites', 'clientid': client_id}
        temp_resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = temp_resp.text

    if data_type == 'device':
        device_type = ('workstation', 'server')
        resp = ''
        for dev_type in device_type:
            payload = {'service': 'list_devices_at_client', 'clientid': client_id, 'devicetype': dev_type}
            temp_resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
            resp += temp_resp.text

    if data_type == 'scan':
        payload = {'service': 'list_mav_scans', 'deviceid': device_id, 'details': 'YES'}
        temp_resp = requests.get('https://%s/api/?apikey=%s&' % (query_server, api_key), params=payload)
        resp = temp_resp.text
        
    return resp

def gen_client_info():
    """Generate Client instances with attribute data"""
    data_type = 'client'
    raw_response = get_response(data_type)
    parsed_data = response.parse(raw_response, data_type)
    create_client_inst(parsed_data)

def gen_site_info():
    """Generate Site data and set attributes in Client instances"""
    data_type = 'site'
    for client_id in Client.inst_by_id.keys(): 
        raw_response = get_response(data_type, client_id)
        parsed_data = response.parse(raw_response, data_type, client_id)
        append_site_info(parsed_data, client_id)

def gen_device_info():
    """Generate Device data and set attributes in Device instances"""
    data_type = 'device'
    for client_id in Client.inst_by_id.keys():
        raw_response = get_response(data_type, client_id)
        parsed_data = response.parse(raw_response, data_type, client_id)
        create_dev_inst(parsed_data, client_id)

def gen_scan_info_all():
    """Generate scan data for each device in Device.inst"""
    for device_id in Device.inst_by_id.keys():
        gen_device_scan_info(device_id)

def gen_device_scan_info(device):
    """Get the threat_dict and append it to the Device instance
        
        Args:
            device : Either device name (str) or device id (int)
    """
    data_type = 'scan'
   
    device_name, device_id = device_id_name(device)
    
    raw_response = get_response(data_type, device_id=device_id)
    parsed_data = response.parse_scan(raw_response, device_id, device_name)
    Device.inst_by_id[device_id].threat_list = parsed_data
    
def scan_from_range(device, date_range):
    """Return the threat_list for a device within a specified range
  
        Args:
            device : Either device name (str) or device id (int)
            date_range (list) : start date end date 
                ['YYYY MM DD', 'YYYY MM DD']
    """
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
    """Provide unknown names or ids for devices. 
    Query user input for either device name or device id, 
    call device_id_name, and then repeat until >quit"""
    disp.device_names(Client.inst_by_name) 
    
    target = raw_input('\n>').lower()
    if target == 'quit':
        exit()
    else:
        print device_id_name(target)
    query_user()

def month_report(client_id, year, month):
    """Return a threat report for the specified client / month
    
        Args:
           client_id (int) = Active clinet ID number
           year (int) = Four digit year
           month (int) = One or two digit month
    """
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
    
    for device_id in Client.inst_by_id[client_id].device_id_dict.keys():
        device_name = device_id_name(device_id)[0]
        dev_threat_list = scan_from_range(device_id, date_range)
        client_threat_dict[device_name] = dev_threat_list
  
    return client_threat_dict

def gen_month_report_doc(client, year, month):
    """Collate and format threat data, call createpdf.build_pdf.

        Args:
            client (str): Active client
            year (int): Four digit year
            month (int): One or two digit month
    """
    client_threat_dict = month_report(client, year, month)
    client_name = client # client name text
    
    root = etree.Element('root')
     
    #root.append( etree.Element('client_name') )
    tag_client_name = etree.SubElement(root, 'client_name')
    tag_client_name.text = client_name
        
    for threat_list in client_threat_dict.values():

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
    # TODO Make this not be hardcoded 
    top_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    report_dir = os.path.join(top_dir, 'threat_reports')

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    out_file = os.path.join(report_dir, '%s.pdf' % filename)
    createpdf.build_pdf(out_file, xml_string) 
    
def all_clients_month_report(year, month):
    """Iterate through all clients and call function to generate 
    report documents
    
        Args:
            year (int): Four digit year
            month (int): One or two digit month
    """
    for client_name in Client.inst_by_name.keys():
       gen_month_report_doc(client_name, year, month)

def populate_database():
    """Call the functions to generate instances and populate them with data"""
    gen_client_info()
    gen_site_info()
    gen_device_info()
    gen_scan_info_all()

def usage():
    """Print basic usage help"""
    print """
Usage: app.py -m MM -y YYYY

Produces .pdf reports for all clients of all threats found during the 
month specified.

Mandatory arguments to long options are mandatory to short form as well.

    -m, --month=MM    Desired month in two digit format, i.e. 07 as July
    -y, --year=YYYY   Desired year in four digit format, i.e. 2015

This module requires a config.ini in the same base folder. The API key 
generated from the dashboard and must be updated if the key is 
regenerated. The server address is found in the Help under 
Integration > Data Extract API. 

The config.ini format is
>>>
    api_key = 32CHARACTERAPIKEYFROMMAXRMDDASHBOARD
    query_server = www.systemmonitor.us
<<<

At present, this module retrieves the client, site, device and MAV scan 
data and produces .pdfs. It can be readily extended to provide 
additional functionality to meet a variety of needs. However, that will 
be up to the end user.

That is to say, this module is provided strictly as-is, has very 
limited error checking and there is no guarantee of support.
    """

def main(argv):
    opts = getConf()
    
    global query_server
    global api_key
    api_key = opts['api_key']
    query_server = opts['query_server']
   
    try:
        options, args = getopt.getopt(argv,'hm:y:',['month=','year='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for option, arg in options:
        if option == '-h':
            usage()
            sys.exit()
        
        elif option in ('-m', '--month'):
            month = int(arg)
        
        elif option in ('-y', '-year'):
            year = int(arg)
    
    print '\nGathering information and building data structures.\nThis will take a moment....'
    
    populate_database()
    
    print '\nCreating threat reports for %s/%s.\nPlease be patient....' % (month, year)
    
    all_clients_month_report(year, month)
   
    print '\nReports completed. Please check the threat_reports destination folder.\n'

    #query_user()

    #disp.client_threats(client_threat_dict, <CLIENTNAME>)
    #disp.clients(Client.inst_by_name)
    #disp.sites(Client.inst_by_id)
    #disp.devices_all(Device.inst_by_name)
    #disp.device_names(Client.inst_by_name)

if __name__ == '__main__':
    main(sys.argv[1:])
