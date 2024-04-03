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
spreadsheet_id = '1jmfy8YhrGAfLE7on9-7kvOQOohVldoVxAW4GIlnyseU'
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
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range='Ryan Sheet!G10:H10').execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        dbObj.updateFuelSalesGasMargin(values[0][0])
        print('Gas Margin: ' + values[0][0])

except HttpError as err:
        print(err)
finally:
    dbObj.closeDB()