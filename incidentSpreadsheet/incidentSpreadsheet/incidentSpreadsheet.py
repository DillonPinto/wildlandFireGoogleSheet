from __future__ import print_function
import httplib2
import os
import itertools

from fnmatch import fnmatch
from datetime import datetime, timedelta
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
dirpath = os.path.dirname(os.path.realpath(__file__))
KEY_PATH =  dirpath + '\SLUGIS-2f3d7647c1b8.json'
SERVICE_EMAIL = 'slugis@slugis-186423.iam.gserviceaccount.com'

LOG_DIR = 'C:/cygwin/home/SLUGIS/documents/' # For production use: //home/coreyf/gst_dashboard/data
VEG_FIRE_CODES = ["FWL", "FWLCD", "FWLG", "FWLH", "FWLL", "FWLM", "FWLMTZ", "FWLT", "FWLZ", "FVCLW", "FVCTW", "FVCW", "FOO", "FOD", "FSRW", "MTC", "FVP", "FOAW"]

def getFile():
    date = datetime.today() - timedelta(days=1)

    logs = (l for l in os.listdir(LOG_DIR) if fnmatch(l, '*_Log.txt'))
    for log in logs:
        date_str = log[0:9]
        log_date = datetime.strptime(date_str, "%Y_%m%d")
        if log_date.date() == date.date():
            print(log)
            return LOG_DIR + log
    
    return

def generateData():
    values = []
    incidents = {}
    n = 0
    # Get previous day log file & open it
    logfile = open(getFile(), 'r') 
    # Read Lines
    for line in logfile:
        # Split the line
        fields = line.split('|')
        if len(fields) > 9 and fields[7] and fields[8]:
            # If it's a vegetation fire, add it to the dictionary of incidents, overwritting previous dispatch of incident
            if fields[5] in VEG_FIRE_CODES:
                if len(fields[2]) < 14:
                    fields[2] = fields[2] + str(n).zfill(14 - len(fields[2]))
                    n += 1
                incidents[fields[2]] = fields

    # might be able to just put incidents.items() where values is in the return,
    # but not sure if items() will return correct format for google api
    for incident, info in incidents.items():
        values.append(info)

    return {'values' : values }

def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet
    """

    # Create service
    credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_PATH, SCOPES)
    http_auth = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http_auth,
                              discoveryServiceUrl=discoveryUrl)

    # Generate values for appending
    body = generateData()
    # Execute append
    sheetId = '12A2DN5RlawDzPz_RfX5jN3YPNSNc6-xD8nVpwqS09is'
    rangeName = 'TestSheet!A:F'
    service.spreadsheets().values().append(
        spreadsheetId=sheetId, range=rangeName, valueInputOption="RAW", body=body, insertDataOption="INSERT_ROWS").execute()


if __name__ == '__main__':
    main()

