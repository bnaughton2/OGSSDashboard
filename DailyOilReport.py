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
from datetime import datetime, timedelta, timezone
import mysql.connector
import uuid
import pytz
import dbcreds as db
from mySQLDB import *

SCOPES = ['https://mail.google.com/']
locale.setlocale(locale.LC_ALL, '')


def insertDailyOilData(data, date):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='OGSS',
                                             user=db.username,
                                             password=db.password)
        cursor = connection.cursor()
        mySql_insert_query = """INSERT INTO DailyOilSales (id, date, invoiceCount, grossAmount, promotionAmount, cogs, marginPercent, netMargin, updatedOn, updatedBy, addedOn, addedBy) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

        updatedOn=addedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        updatedBy=addedBy = "OGSS Web Server"
        id = str(uuid.uuid4())
        record = (id, date, data[0], data[1], data[2], data[3], data[4], data[5], updatedOn, updatedBy, addedOn, addedBy)
        cursor.execute(mySql_insert_query, record)
        connection.commit()
        print("Record inserted successfully into DailyOilSales table")

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def formatCurrency(string):
    if string.strip('"') == '':
        return 0.0
    else:
        return float(string.strip('"').strip('$').replace(',',''))

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

def formatDailyOilDate(string):
    date = string[:-12]
    date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S')
    date = date - timedelta(days=1)
    date = date.strftime('%Y-%m-%d')
    return date

def formatDailyOilData(string):
    lines = string.decode('UTF-8')
    linesSplit = lines.split('\n')[2].split('\t')
    invoiceCount = formatNumber(linesSplit[1])
    grossAmount = formatCurrency(linesSplit[2])
    promotionAmount = formatCurrency(linesSplit[10])
    cogs = formatCurrency(linesSplit[7])
    marginPercent = formatPercent(linesSplit[9])
    netMargin = formatCurrency(linesSplit[8])
    out = [invoiceCount, grossAmount, promotionAmount, cogs, marginPercent, netMargin]
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
    dbObj = DB()
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
                        if values['value'] == 'Daily Oil Report':
                            try:
                                attachment_id = msg['payload']['parts'][-1]['body']['attachmentId']
                                attachment = service.users().messages().attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                                data = attachment.get("data")
                                date = formatDailyOilDate(getValueFromEmailData(email_data, 'Date'))
                                #Insert data into database
                                dbObj.insertDailyOilData(formatDailyOilData(urlsafe_b64decode(data)), date)
                                #Set email to rea then move to trash
                                msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                msg = service.users().messages().trash(userId='me', id=message['id']).execute()
                            except BaseException as error:
                                print("Daily Oil Report:" + str(error))
                                #email error to notify issue

    except Exception as error:
        print(f'An error occurred: {error}')
    dbObj.closeDB()

readEmails()