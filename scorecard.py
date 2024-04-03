import os.path
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import requests
from base64 import urlsafe_b64decode, urlsafe_b64encode
from mySQLDB import *

dbObj = DB()

# spreadsheet_id = '1eiXPzdqiAJkbr0tTuzucukazREPPDxkjDP7bwFSYqjM'
spreadsheet_id = '1P9qitKl9NLnyivJjgwuJhCpMrw4oSgZ08G01mA7Xn8M'
SCOPES = ['https://mail.google.com/', "https://www.googleapis.com/auth/spreadsheets.readonly"]
# For example:
creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(               
            # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
            'client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
try:
    service = build("sheets", "v4", credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().batchGet(spreadsheetId=spreadsheet_id,
                                ranges=['KPI Dashboard!C9', 'KPI Dashboard!C11', 'KPI Dashboard!C15', 'KPI Dashboard!C17', 'KPI Dashboard!E9', 'KPI Dashboard!E11', 'KPI Dashboard!E15', 'KPI Dashboard!E17']).execute()
    valueRanges = result.get('valueRanges', [])

    if not valueRanges:
        print('No data found.')
    else:
        data = []
        for i in valueRanges:
            data.append(i['values'][0][0])
        dbObj.upsertScorecardData(data)

except HttpError as err:
        print(err)
finally:
    dbObj.closeDB()