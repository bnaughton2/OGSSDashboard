from datetime import datetime, timedelta
from mySQLDB import *
import requests
import json

def fetchReviews():
    url = "https://serpapi.com/search.json?q=old+greenwich+service+station&location=United+States&hl=en&gl=us&api_key=8c7afed337d7082af4e3c0d0ee21225635ecf4b72ae375e155d975ccb47f3589&async=true"
    key = '8c7afed337d7082af4e3c0d0ee21225635ecf4b72ae375e155d975ccb47f3589'
    response = requests.get(url)

    googleRating = 0
    googleReviewCount = 0
    otherRating = 0
    otherReviewCount = 0
    if response.ok:
        pyObj = json.loads(response.content)
        googleRating += float(pyObj['knowledge_graph']['rating'])
        googleReviewCount += pyObj['knowledge_graph']['review_count']
        otherRating += float(pyObj['knowledge_graph']['reviews_from_the_web'][0]['rating'])
        otherReviewCount += pyObj['knowledge_graph']['reviews_from_the_web'][0]['review_count']
        print(f"{googleRating} | {googleReviewCount} | {otherRating} | {otherReviewCount}")
        return [round((googleRating + otherRating)/2, 3), googleReviewCount + otherReviewCount]
    else:
        print("Invalid status code")
        return [-1,-1]

def main():
    try:
        dbObj = DB()
        time = datetime.now()
        now = time.strftime('%Y-%m-%d')
        print("Start Time: "+ time.strftime('%Y-%m-%d %H:%M:%S'))
        data = fetchReviews()
        print(data)
        if data != [-1,-1]:
            dbObj.insertReviewData(data, now)
    except:
        print("Something went wrong in reviews.py")
    finally:
        dbObj.closeDB()


if __name__ == "__main__":
    main()