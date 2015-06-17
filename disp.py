#! /usr/bin/python2

# Python 2.7
"""Display information gathered by queryMAXrm.py to the console in a resonable manner.""" 

def clients(Client):
    """Iterate over Clients.inst_by_name and display client names and IDs"""
    print '\n***Name : ID***'
    for inst in Client.inst_by_name.values():
        print '\n%s : %s' %(inst.name, inst.id)


def sites(Client):
    """Iterate over site_name_dict for each Client.inst_by_name.value and
    display site names and IDs
    """
    print '\n***Name : ID***'
    for inst in Client.inst_by_name.values():
        print '\n%s : %s' % (inst.name, inst.id)

        for key in inst.site_name_dict.keys():
            print '\t%s : %s' % (key, inst.site_name_dict[key])

def devices_all(Device):
    """Iterate over Device.inst_by_name and display device names and IDs"""
    print '\n***Name : ID***\n'
    for inst in Device.inst_by_name.values():
        print '%s : %s' % (inst.name, inst.id)

def device_names(Client, Device):
    """Display device names in three columns"""
    client_dict = {}
    
    for client_inst in Client.inst_by_name.values():
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

