from bs4 import BeautifulSoup as bsoup
def parse(data, data_type, client_id=None):
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


def parse_scan(data, device_id, device_name):
    """Accept raw response, pull out desired threat data and return parsed response data"""

    #This block is only for testing. 
    # Remove and confirm correct function of https GET before deploy
    if data == None:
        filename = './data/scans/%s_scandata' % (device_id)
        with open(filename, 'r') as f:
            response_data = f.read()
            f.close()

        soup = bsoup(response_data, 'html5lib')
    
    else:
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
