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
from dateutil import tz
import mysql.connector
import uuid
import pytz
import io
import pandas as pd
import numpy as np
import dbcreds as creds
from mySQLDB import *
import json
from lxml import etree
import csv
import unidecode

SCOPES = ['https://mail.google.com/', "https://www.googleapis.com/auth/spreadsheets.readonly"]
locale.setlocale(locale.LC_ALL, '')


def replaceCommas(string, char):
    inQuotes = False
    out = ''
    for y in string:
        if y == '"' and (inQuotes == False):
            inQuotes = True
        elif y == '"' and (inQuotes == True):
            inQuotes = False
        elif y == ',' and inQuotes == False:
            out = out+char
        else:
            out = out+y
    return out

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

def formatWholeNumber(string):
    if string.strip('"') == '':
        return 0
    else:
        tmp = string.strip('"').replace(',','')
        return int(tmp)

def formatString(string):
    if string.strip('"') == '':
        return ''
    else:
        tmp = string.strip('"')
        return str(tmp)

def formatConnectTeamDateTime(string):
    date = string[:-6]
    date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    return date

def formatVendingDate(string):
    tmp = string[:-6]
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    utc = datetime.strptime(tmp, '%d %b %Y %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    date = local.strftime('%Y-%m-%d %H:%M:%S')
    return date

def formatISIDate(string):
    tmp = string[:-12]
    local = pytz.timezone('America/Los_Angeles')
    naive = datetime.strptime(tmp, '%a, %d %b %Y %H:%M:%S')
    print(f"Naive: {naive}")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    date = naive.strftime('%Y-%m-%d')
    return date

def formatWashconnectDate(string):
    tmp = string[:-6]
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    utc = datetime.strptime(tmp, '%a, %d %b %Y %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    date = local.strftime('%Y-%m-%d %H')
    return date

def formatDailyOilDate(string):
    date = string[:-12]
    date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S')
    date = date - timedelta(days=1)
    date = date.strftime('%Y-%m-%d')
    return date

def formatRealTimeOilData(string):
    lines = string.decode('UTF-8')
    linesSplit = lines.split('\n')[1].split('\t')
    storeAlias = formatString(linesSplit[1])
    if storeAlias == 'New England Service Corp. #1 2577':
        grossSales = formatCurrency(linesSplit[4])
        promotionAmount = formatCurrency(linesSplit[7])
        #grossSales - Promotions = NetSales
        return [grossSales, promotionAmount]
    else:
        return "Invalid Email Data"

def formatDailyOilData(string):
    lines = string.decode('UTF-8')
    linesSplit = lines.split('\n')[2].split('\t')
    invoiceCount = formatWholeNumber(linesSplit[1])
    grossAmount = formatCurrency(linesSplit[2])
    promotionAmount = formatCurrency(linesSplit[10])
    cogs = formatCurrency(linesSplit[7])
    marginPercent = formatPercent(linesSplit[9])
    netMargin = formatCurrency(linesSplit[8])
    out = [invoiceCount, grossAmount, promotionAmount, cogs, marginPercent, netMargin]
    return out

def formatClubSummaryData(string):
    lines = string.decode('UTF-8')
    linesSplit = replaceCommas(lines, '\t').split('\r\n')
    arr = []
    for r in linesSplit:
        arr.append(r.split('\t'))
    ind = None
    for x in arr:
        for i,j in enumerate(x):
            if j == 'Textbox76':
                ind = i
        if ind is not None:
            return formatWholeNumber(arr[1][ind]) 
    return -1

def formatShiftRegisterData(string):
    lines = string.decode('UTF-8')
    linesSplit = replaceCommas(lines, '\t').split('\r\n')
    arr = []
    for r in linesSplit:
        arr.append(r.split('\t'))
    totalWashSales = ''
    for i,x in enumerate(arr):
        if x[0] == 'Total Sales:':
            return formatCurrency(x[1])
    return -1

def getValueFromEmailData(emailData, value):
    out = ''
    for x in emailData:
        val = x['name']
        if val == value:
            out = x['value']
    return out

def getValueFromDF(df, string, colNum, cast, step=1):
    out = 0
    columnSeriesObj = df.iloc[:, colNum]
    nextObj = df.iloc[:, colNum+step]
    for idx, val in np.ndenumerate(columnSeriesObj.values):
        if val == string:
            out = nextObj.values[idx[0]]
            # print(f"{idx[0]}: {val} | Next: {out}")
            break
    if type(out) == str:
        out = out.replace(",", "").strip('()').strip('$')
    return cast(out)

def readEmails():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    dbObj = DB()
    creds = None
    wash = {}
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
                email_data = msg['payload']['headers']
                for values in email_data:
                    value = values['name']
                    date = ''
                    if value == 'Subject':
                        if values['value'] == 'Real-Time Oil Sales':
                            try:
                                attachment_id = msg['payload']['parts'][-1]['body']['attachmentId']
                                attachment = service.users().messages().attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                                data = attachment.get("data")
                                data = formatRealTimeOilData(urlsafe_b64decode(data))
                                date = formatISIDate(getValueFromEmailData(email_data, 'Date'))
                                #insert data into database
                                if data != "Invalid Email Data":
                                    dbObj.upsertRealTimeOilData(data, date)
                                #Set Email as read and then move to trash
                                msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                msg = service.users().messages().trash(userId='me', id=message['id']).execute()
                            except BaseException as error:
                                print("Real Time Oil: " + str(error))
                                #email error to notify issue
                    elif value == 'From':
                        if values['value'] == 'noreply@eposnow.com':
                            try:
                                date = formatConnectTeamDateTime(getValueFromEmailData(email_data, 'Date'))
                                subject = getValueFromEmailData(email_data, 'Subject')
                                if "Lottery Sales" in subject:
                                    body = msg['payload']['parts'][0]['body']['data']
                                    data = base64.urlsafe_b64decode(body.encode('UTF-8'))
                                    tables = pd.read_html(data)
                                    table = tables[0]
                                    saleArr = table[table[0].str.contains('Total Sales', na=False)].head(1)[0].item()
                                    saleArr = saleArr.split()
                                    lottoSales = formatCurrency(saleArr[2])
                                    dbObj.updateLotterySales(lottoSales, date)
                                    msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                    msg = service.users().messages().trash(userId='me', id=message['id']).execute()
                                else:
                                    body = msg['payload']['parts'][0]['body']['data']
                                    data = base64.urlsafe_b64decode(body.encode('UTF-8'))
                                    tables = pd.read_html(data)
                                    table = tables[0]
                            except BaseException as error:
                                print("Error in lottery insert: " + str(error))
                        elif values['value'] == 'notifier@nayax.com':
                            try:
                                date = formatVendingDate(getValueFromEmailData(email_data, 'Date'))
                                attachment_id = msg['payload']['parts'][-1]['body']['attachmentId']  
                                attachment = service.users().messages().attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                                data = attachment.get("data")
                                data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                                tables = pd.read_html(data) 
                                table = tables[0]
                                sales = table.tail(1)["Today's Credit Card Sales"].item()
                                vends = table.tail(1)["Today's Credit Card Vends"].item()
                                totalSales = sales + vends
                                dbObj.updateVendingSales(totalSales, date)
                                msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                msg = service.users().messages().trash(userId='me', id=message['id']).execute()
                            except BaseException as error:
                                print("Error in vacuum/vending insert: " + str(error))
                        elif values['value'] == 'data@fastcw.com':
                            try:
                                attachment_id = msg['payload']['parts'][1]['body']['attachmentId']
                                attachment = service.users().messages().attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                                data = attachment.get("data")
                                data = urlsafe_b64decode(data)
                                json_data = json.loads(data)
                                alerts = json_data['Alerts']
                                for i in alerts:
                                    dbObj.insertWaitTimeData(i)
                                msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                msg = service.users().messages().trash(userId='me', id=message['id']).execute()
                            except BaseException as error:
                                print("Error in wait time insert: " + str(error))
                        elif values['value'] == 'Old Greenwich Service Station App <noreply@reports.connecteam.com>':
                            date = getValueFromEmailData(email_data, 'Date')
                            subject = getValueFromEmailData(email_data, 'Subject')
                            body = getValueFromEmailData(email_data, 'Body')
                            if "Emmissions Daily Paperwork" in subject:
                                try:
                                    date = formatConnectTeamDateTime(getValueFromEmailData(email_data, 'Date'))
                                    attachment_id = msg['payload']['parts'][-1]['body']['attachmentId'] 
                                    attachment = service.users().messages().attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                                    data = attachment.get("data")
                                    data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                                    tables = pd.read_excel(io.BytesIO(data)) 
                                    emmissionsDone = tables['How Many Emmissions were preformed today?'][0].item()
                                    vinChecksDone = tables['How many VIN checks today?'][0].item()
                                    dbObj.updateEmmissionsDone(emmissionsDone, date)
                                    dbObj.updateVinChecksDone(vinChecksDone, date)
                                    msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                    msg = service.users().messages().trash(userId='me', id=message['id']).execute()
                                except BaseException as error:
                                    print("Error inserting Emissions data: " + str(error))
                            else:
                                arr = subject.split(' completed ')
                                if subject == "Old Greenwich Service Station's daily report for Bought/Returned Credit Card Form - Auto report":
                                    # print(msg['payload'])
                                    try:
                                        attachment_id = msg['payload']['parts'][-1]['body']['attachmentId']
                                        attachment = service.users().messages().attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                                        data = attachment.get("data")
                                        data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                                        tables = pd.read_excel(io.BytesIO(data))
                                        date = tables['Submission Date'][0]
                                        if 'Which department are you?' in tables.columns:
                                            dept = tables['Which department are you?'][0]
                                        else:
                                            dept = tables['Which department / Site are you?'][0]
                                        amount = tables['Total Amount:'][0]
                                        data = {"dept": str(dept), "amount": float(amount)}
                                        dbObj.insertDamageData(data, str(date))
                                        msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                        msg = service.users().messages().trash(userId='me', id=message['id']).execute()
                                    except BaseException as error:
                                        print("Error inserting Damagages data: " + str(error))
                                else:
                                    try:
                                        if(arr[1] == 'Check-Ins' or arr[1] == 'Check-Ins '):
                                            data = [unidecode.unidecode(arr[0]), arr[1], arr[1]]
                                        else:
                                            data = [unidecode.unidecode(arr[0]), arr[1], arr[1].split()[:2]]
                                        date = formatConnectTeamDateTime(date)
                                        #insert data into database
                                        dbObj.insertConnectTeamData(data, date)
                                        #Set Email as read and then move to trash
                                        msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                        msg = service.users().messages().trash(userId='me', id=message['id']).execute()
                                    except BaseException as error:
                                        print("Error inserting ConnectTeam data: " + str(error))
                                    
                        elif values['value'] == 'MyReports@washconnect.com' or values['value'] == 'MyReports@washac1.com':
                            date = getValueFromEmailData(email_data, 'Date')
                            subject = getValueFromEmailData(email_data, 'Subject')
                            try:
                                if "ClubSummary was executed at" in subject:
                                    attachment_id = msg['payload']['parts'][1]['parts'][0]['body']['attachmentId']
                                    attachment = service.users().messages().attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                                    data = attachment.get("data")
                                    members = formatClubSummaryData(urlsafe_b64decode(data))
                                    wash['club'] = {"date": formatWashconnectDate(date), "members": members} 
                                    #Set Email as read and then move to trash
                                    msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                    msg = service.users().messages().trash(userId='me', id=message['id']).execute()
                                if "Shift Register Cube was executed at" in subject:
                                    attachment_id = msg['payload']['parts'][1]['parts'][0]['body']['attachmentId']
                                    attachment = service.users().messages().attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                                    data = attachment.get("data")
                                    data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                                    tables = pd.read_csv(io.BytesIO(data), sep=',', header=None, names=list(range(25))).dropna(axis='columns', how='all')
                                    washesSold = getValueFromDF(tables, 'Ultimate', 9, int) + getValueFromDF(tables, 'Works', 9, int) + getValueFromDF(tables, 'Express', 9, int)
                                    washesRedeemed = getValueFromDF(tables, 'Club Unlimited Redeemed', 9, int)
                                    membershipsSold = getValueFromDF(tables, 'Total Sold', 16, int)
                                    totalSales = getValueFromDF(tables, 'Total Sales:', 0, str)
                                    paidAtPump = getValueFromDF(tables, 'Paid in store', 16, float, 2)
                                    print(f"Paid at pump: {paidAtPump}")
                                    wash['reg'] = {"date":  formatWashconnectDate(date), "sales": formatCurrency(totalSales), "washesSold": washesSold, "washesRedeemed": washesRedeemed, "membershipsSold": membershipsSold, "paidAtPump": paidAtPump}
                                    #Quantity of carwash memberships purchased + individual carwashes purchased
                                    #Set Email as read and then move to trash
                                    msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                    msg = service.users().messages().trash(userId='me', id=message['id']).execute()
                                if(wash != {} and wash['club']['date'] == wash['reg']['date']):
                                    #Upsert into DB
                                    print(wash)
                                    dbObj.upsertCarwashData(wash)
                                    dbObj.insertHourlyCarwashData(wash)
                                    wash = {}
                            except BaseException as error:
                                print("Error inserting Car wash data: " + str(error))
                        elif values['value'] == '"admin@rsmgt.net" <admin@rsmgt.net>':
                            date = getValueFromEmailData(email_data, 'Date')
                            subject = getValueFromEmailData(email_data, 'Subject')
                            try:
                                data = formatCurrency(subject)
                                dbObj.insertPayrollData(data)
                                #Set Email as read and then move to trash
                                msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                msg = service.users().messages().trash(userId='me', id=message['id']).execute()
                            except BaseException as error:
                                print("Payroll/Admin@rsmgt.net: " + str(error))
    except Exception as error:
        print(f'An error occurred: {error}')
    dbObj.closeDB()

readEmails()
