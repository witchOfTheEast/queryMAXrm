#! /usr/bin/python2

# Python 2.7
"""Display information gathered by queryMAXrm.py to the console in a resonable manner.""" 

def clients(inst_dict):
    """Iterate over dict of Client instances and display client names and IDs.

        Args: 
            inst_dict (dict) : Dictionary of client instances
    """
    print '\n***Name : ID***'
    for inst in inst_dict.values():
        print '\n%s : %s' %(inst.name, inst.id)


def sites(inst_dict):
    """Iterate over dict of Client instances.site_name_dict and
    display site names and IDs

        Args: 
            inst_dict (dict) : Dictionary of client instances
    """
    print '\n***Name : ID***'
    for inst in inst_dict.values():
        print '\n%s : %s' % (inst.name, inst.id)

        for key in inst.site_name_dict.keys():
            print '\t%s : %s' % (key, inst.site_name_dict[key])

def devices_all(inst_dict):
    """Iterate over Device instances and display device names and IDs.

        Args: 
            inst_dict (dict) : Dictionary of Device instances
    """
    print '\n***Name : ID***\n'
    for inst in inst_dict.values():
        print '%s : %s' % (inst.name, inst.id)

def device_names(inst_dict):
    """Display device names in three columns

        Args:
            inst_dict (dict) : Dictionary of Client instances
    """
    client_dict = {}
    
    for client_inst in inst_dict.values():
        client_name = client_inst.name
        name_list = []
        for device_name in client_inst.device_name_dict.keys():
            name_list.append(device_name)
        
        client_dict[client_name] = name_list

    for client_name in client_dict.keys():
        name_rows = []
        name_list = client_dict[client_name]
        print '\n***%s %s devices***' % (client_name, len(name_list))

        i = 0
        while i < len(name_list):
            name_rows.append(name_list[i:i+6])
            i += 6  
     
        col_width = max(len(device_name) for row in name_rows for device_name in row) + 1 # padding
        for row in name_rows:
            print ''.join(word.ljust(col_width) for word in row)

def threats(threat_list):
    """Display the threat_dict data is a resonable way
    
        Args:
            threat_list (list) : Minimum length is 1. Device name at index[0],
                followed by a dictionary for each threat, if any, at index[1:].
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

def client_threats(client_threat_dict, client_name):
    """Take a client_threat_dict and display threat information
    
        Args:
            client_threat_dict (dict) : Keys are device_names and values are threat_lists
            client (str) : Target client name
    """
    print 'Threats for client %s' % client_name
    for device in client_threat_dict.keys():
        threats(client_threat_dict[device])
