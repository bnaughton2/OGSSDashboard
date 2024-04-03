from /home/ec2-user/OGSSDashboard/mySQLDB import *


def selectStoreSalesOnDate(self, date):
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM StoreSales WHERE DATE(date) = %s"""
            d = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d')
            queryParams = (d,)
            cursor.execute(mySql_select_query, queryParams)
            result = cursor.fetchone()
            cursor.reset()
            return result
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))

def main():
    dbObj = DB()


if __name__ == "__main__":
    main()