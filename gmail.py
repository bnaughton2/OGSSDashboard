import os.path
import base64
import json
import re
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging
import requests
from base64 import urlsafe_b64decode, urlsafe_b64encode
import locale
from datetime import datetime, timedelta
import mysql.connector

SCOPES = ['https://mail.google.com/']
locale.setlocale(locale.LC_ALL, '')

def formatCurrency(string):
    if string.strip('"') == '':
        return 0.0
    else:
        return float(locale.atof(string.strip('"').strip('$')))

def formatPercent(string):
    if string.strip('"') == '':
        return 0.0
    else:
        tmp = string.strip('"').strip('%')
        return float(tmp) / 100

def formatNumber(string):
    if string.strip('"') == '':
        return 0
    else:
        tmp = string.strip('"')
        return int(tmp)

def formatString(string):
    if string.strip('"') == '':
        return ''
    else:
        tmp = string.strip('"')
        return str(tmp)

def formatDateTime(string):
    date = string[:25]
    date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    return date

def formatDailyOilDateTime(string):
    date = string[:25]
    print(date)
    date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S')
    date = date - timedelta(days=1)
    date = date.strftime('%Y-%m-%d %H:%M:%S')
    return date

def formatRealTimeOilData(string):
    lines = string.decode('UTF-8')
    linesSplit = lines.split('\n')[1].split('\t')
    storeAlias = formatString(linesSplit[1])
    if storeAlias == 'New England Service Corp. #1 2577':
        grossSales = formatCurrency(linesSplit[4])
        promotions = formatCurrency(linesSplit[7])
        #grossSales - Promotions = NetSales
        return grossSales
    else:
        return "Invalid Email Data"

def formatDailyOilData(string):
    lines = string.decode('UTF-8')
    linesSplit = lines.split('\n')[2].split('\t')
    invoiceCount = formatNumber(linesSplit[1])
    grossAmount = formatCurrency(linesSplit[2])
    promotionAmount = formatCurrency(linesSplit[10])
    cogs = formatCurrency(linesSplit[7])
    marginPercent = formatPercent(linesSplit[9])
    netMargin = formatCurrency(linesSplit[8])
    out = [netMargin, marginPercent]
    return out

def getValueFromEmailData(emailData, value):
    out = ''
    for x in emailData:
        val = x['name']
        if val == value:
            out = x['value']
    return out

def readEmails():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages',[])
        if not messages:
            print('No new messages.')
        else:
            message_count = 0
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                # delete = service.users().messages().delete(userId='me', id=message['id']).execute()
                email_data = msg['payload']['headers']
                for values in email_data:
                    value = values['name']
                    date = ''
                    if value == 'Subject':
                        if values['value'] == 'Real-Time Oil Sales':
                            try:
                                attachment_id = msg['payload']['parts'][1]['body']['attachmentId']
                                attachment = service.users().messages().attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                                data = attachment.get("data")
                                date = getValueFromEmailData(email_data, 'Date')
                                date = formatDateTime(date)
                                #insert data into database
                                #delete email
                                # msg = service.users().messages().delete(userId='me', id=message['id']).execute()
                                print(formatRealTimeOilData(urlsafe_b64decode(data)))
                            except BaseException as error:
                                print(error)
                                #email error to notify issue
                        if values['value'] == 'Daily Oil Report':
                            try:
                                attachment_id = msg['payload']['parts'][1]['body']['attachmentId']
                                attachment = service.users().messages().attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                                data = attachment.get("data")
                                date = getValueFromEmailData(email_data, 'Date')
                                date = formatDailyOilDateTime(date)
                                print(date)
                                #insert data into database
                                #delete email
                                # msg = service.users().messages().delete(userId='me', id=message['id']).execute()
                                print(formatDailyOilData(urlsafe_b64decode(data)))
                            except BaseException as error:
                                print(error)
                                #email error to notify issue
                            
                    elif value == 'From':
                        try:
                            if values['value'] == 'Old Greenwich Service Station App <noreply@reports.connecteam.com>':
                                date = getValueFromEmailData(email_data, 'Date')
                                subject = getValueFromEmailData(email_data, 'Subject')
                                arr = subject.split(' completed ')
                                person = arr[0]
                                fullTask = arr[1]
                                action = fullTask.split()[:2]
                                date = formatDateTime(date)
                                #insert data into database
                                #delete email
                                print(person)
                                print(fullTask)
                                print(action)
                                print(date)

                        except BaseException as error:
                            print(error)
    except Exception as error:
        print(f'An error occurred: {error}')

readEmails()