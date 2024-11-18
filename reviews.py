from datetime import datetime, timedelta
from mySQLDB import *
import requests
import json

def fetchReviews():
    key = '8c7afed337d7082af4e3c0d0ee21225635ecf4b72ae375e155d975ccb47f3589'
    oilUrl = f"https://serpapi.com/search.json?q=mobil+1+oil+change+old+greenwich&oq=mobil+1+oil+change+old+greenwich&hl=en&gl=us&api_key={key}&async=true"
    gasUrl = f"https://serpapi.com/search.json?q=shell+gas+station+old+greenwich&oq=shell+gas+station+old+greenwich&hl=en&gl=us&api_key={key}&async=true"
    washUrl = f"https://serpapi.com/search.json?q=shell+car+wash+old+greenwich&oq=shell+car+wash+old+greenwich&hl=en&gl=us&api_key={key}&async=true"

    r1 = requests.get(oilUrl)
    r2 = requests.get(gasUrl)
    r3 = requests.get(washUrl)
    # print(str(r1) + ' | ' + str(r1.content))
    # print(str(r2) + ' | ' + str(r2.content))
    print(str(r3) + ' | ' + str(r3.content))

    if r1.ok and r2.ok and r3.ok:
        print("In if statement")
        oilObj = json.loads(r1.content)
        gasObj = json.loads(r2.content)
        washObj = json.loads(r3.content)
        data = {"oil": {}, "gas": {}, "wash": {}}
        data['oil'] = {"rating": float(oilObj['knowledge_graph']['rating']), "count": oilObj['knowledge_graph']['review_count']}
        data['gas'] = {"rating": float(gasObj['knowledge_graph']['rating']), "count": gasObj['knowledge_graph']['review_count']}
        data['wash'] = {"rating": float(washObj['knowledge_graph']['rating']), "count": washObj['knowledge_graph']['review_count']}
        print(data)
        return data
    else:
        print("Invalid status code")
        return {}

def main():
    try:
        dbObj = DB()
        time = datetime.now()
        now = time.strftime('%Y-%m-%d')
        print("Start Time: "+ time.strftime('%Y-%m-%d %H:%M:%S'))
        data = fetchReviews()
        if data != {}:
            dbObj.insertReviewData(data, now)
    except BaseException as error:
        print("Something went wrong in reviews.py | " + str(error))
    finally:
        dbObj.closeDB()


if __name__ == "__main__":
    main()