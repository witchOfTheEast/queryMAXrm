# Python 2.7
from bs4 import BeautifulSoup as bsoup
"""Provide parsing for various types of http response data"""
def parse(data, data_type, client_id=None):
    """Extract data from raw response and return parsed dicts in
    a tuple
        Args:
            data: GET response data
            data_type (str): 'client', 'site', device', but not 'scan'
            client_id (int): Active client ID number
    """
    if data_type == 'client':
        search_1 = 'name'
        search_2 = 'clientid'

    elif data_type == 'site':
        search_1 = 'name'
        search_2 = 'siteid'

    elif data_type == 'device':
        search_1 = ['workstation', 'server'] 
        search_2 = 'id'
    
    elif data_type == 'mavscan':
        pass 
    
    soup = bsoup(data, 'html5lib')
    
    result_1 = soup.find_all(search_1)
    result_2 = soup.find_all(search_2)
    
    if len(result_1) != len(result_2):
        pass 
    
    return (result_1, result_2, data_type)

def parse_scan(data, device_id, device_name):
    """Extract data from raw response and return parsed dicts in
    a tuple
        Args:
            data: GET response data
            device_id (int): Active device ID number
            device_name (str): Active device name
    """
    
    soup = bsoup(data, 'html5lib')

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
        
        threat_dict['traces'] = trace_list

        threat_list.append(threat_dict)

    return threat_list
