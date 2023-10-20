import locale
from datetime import datetime, timedelta
import pytz
# locale.setlocale(locale.LC_ALL, '')

# string = b'"Store Number"\t"Store Alias"\t"Tickets"\t"Store Tickets"\t"Gross Sales"\t"Net Sales"\t"Gross Profit"\t"Promotions"\t"Wages"\t"Commissions"\t"Labor % Gross"\t"Labor % Net"\t"COGS"\t"COGS % Gross"\t"COGS % Net"\n"1"\t"New England Service Corp. #1 2577"\t"55"\t"18"\t"$6,229.52"\t"$6,144.52"\t"($672,716.55)"\t"$85.00"\t"$141.00"\t"$384.90"\t"8.44%"\t"8.56%"\t"$678,335.17"\t"10,889.04%"\t"11,039.68%"\n"Total"\t""\t"55"\t"18"\t"$6,229.52"\t"$6,144.52"\t"($672,716.55)"\t"$85.00"\t"$141.00"\t"$384.90"\t"8.44%"\t"8.56%"\t"$678,335.17"\t"10,889.04%"\t"11,039.68%"\n'

# daily = b'""\t""\t"Gross"\t"Gross"\t""\t"Net"\t"Net"\t"Net"\t"Net"\t"Net"\t""\t""\n""\t"Invoice Count"\t"Gross Amount"\t"Ticket Average"\t""\t"Net Amount"\t"Ticket Average"\t"Cost of Goods Sold Amount"\t"Margin"\t"Margin %"\t"Promotion Amount"\t"Promotion %"\n"All Invoices"\t"52"\t"$5,972.77"\t"$114.86"\t""\t"$5,877.77"\t"$113.03"\t"$2,242.87"\t"$3,634.90"\t"62%"\t"$95.00"\t"2%"\n"w/o E-Mail"\t"52"\t"$5,972.77"\t"$114.86"\t""\t"$5,877.77"\t"$113.03"\t"$2,242.87"\t"$3,634.90"\t"62%"\t"$95.00"\t"2%"\n"Promotion"\t"10"\t"$1,379.07"\t"$137.91"\t""\t"$1,284.07"\t"$128.41"\t"$870.03"\t"$414.04"\t"32%"\t"$95.00"\t"7%"\n"w/o promotion"\t"42"\t"$4,593.70"\t"$109.37"\t""\t"$4,593.70"\t"$109.37"\t"$1,372.84"\t"$3,220.86"\t"70%"\t"$0.00"\t"0%"\n"Fleet"\t"1"\t"$56.98"\t"$56.98"\t""\t"$56.98"\t"$56.98"\t"$9.68"\t"$47.30"\t"83%"\t"$0.00"\t"0%"\n"w/o Fleet"\t"51"\t"$5,915.79"\t"$116.00"\t""\t"$5,820.79"\t"$114.13"\t"$2,233.19"\t"$3,587.60"\t"62%"\t"$95.00"\t"2%"\n'

# lines = daily.decode('UTF-8')
# linesSplit = lines.split('\n')[2].split('\t')
# netMargin = linesSplit[8]
# marginPercent = linesSplit[9]
# print(marginPercent)
# marginPercent = marginPercent.strip('"').strip('%')
# marginPercent = float(marginPercent) / 100
# print(netMargin)
# print(marginPercent)
# netSales = lines.split('\n')[1].split('\t')[5]

# print(float(locale.atof(netSales.strip('"').strip('$'))))

# for part in msg['payload']['parts']:
#     try:
#         body = part.get("body")

#         data = part['body']["data"]
#         byte_code = base64.urlsafe_b64decode(data)

#         text = byte_code.decode("utf-8")
#         print ("This is the message: "+ str(text))

#         # mark the message as read (optional)
#         msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                                                                
#     except BaseException as error:
#         pass

def formatDate(string):
    local = pytz.timezone('America/New_York')
    date = datetime.strptime(string+"  06:00:00", '%m/%d/%Y %H:%M:%S')
    local_dt = local.localize(date, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    date = utc_dt.strftime('%Y-%m-%d %H:%M:%S')
    return date

print(formatDate('10/19/2023'))