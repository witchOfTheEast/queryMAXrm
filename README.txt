Installation

1.) Install Python 2.7.X, with pip and setuptools (included by default)
2.) Download queryMAXrm-0.1.zip
3.) To setup the package and install all the dependencies, in the command line nagivate to the download folder and run: 
    pip install queryMAXrm-0.1.zip
    
4.) Extract queryMAXrm-0.1.zip to destination directory
5.) From command line, nagivate to destination directory and run:
    python queryMAXrm\app.py -m MM -y YYYY
6.) Look for report .pdfs in the destination\threat_reports folder

Ex: 
-extracted to C:\Users\temp\scripts\
-created C:\Users\temp\scripts\queryMAXrm-0.1
-nagivate the command line to C:\Users\temp\scripts\queryMAXrm-0.1
-run: python queryMAXrm\runme.py -m 05 -y 2015
-reports created in C:\Users\temp\scripts\queryMAXrm-0.1\threat_reports


Usage: <SCRIPT> -m MM -y YYYY

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
    api_key = 32CHARACTERAPIKEYFROMMAXRMDASHBOARD
    query_server = www.systemmonitor.us
<<<

At present, this module retrieves the client, site, device and MAV scan 
data and produces .pdfs. It can be readily extended to provide 
additional functionality to meet a variety of needs. However, that will 
be up to the end user.

That is to say, this module is provided strictly as-is, has very 
limited error checking and there is no guarantee of support.
 
