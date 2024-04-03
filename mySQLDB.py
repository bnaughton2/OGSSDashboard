import mysql.connector
import uuid
import pytz
import dbcreds as creds
from base64 import urlsafe_b64decode, urlsafe_b64encode
import locale
from datetime import datetime, timedelta, timezone

class DB:
    def __init__(self):
        self.db = self.initDB()

    def insertDailyOilData(self, data, date):
        try:
            cursor = self.db.cursor()
            mySql_insert_query = """INSERT INTO DailyOilSales (id, date, invoiceCount, grossAmount, promotionAmount, cogs, marginPercent, netMargin, oilMargin, updatedOn, updatedBy, addedOn, addedBy) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

            updatedOn=addedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            updatedBy=addedBy = "OGSS Web Server"
            oilMargin = self.selectValueFromAppParams('oil')
            id = str(uuid.uuid4())
            record = (id, date, data[0], data[1], data[2], data[3], data[4], data[5], oilMargin, updatedOn, updatedBy, addedOn, addedBy)
            cursor.execute(mySql_insert_query, record)
            self.db.commit()
            print("Record inserted successfully into DailyOilSales table")

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def insertWaitTimeData(self, data):
        try:
            recentWait = self.selectRecentWaitTimesForDepartment(str(data['line']))[3]
            d = datetime.fromisoformat(data['timestamp'][:-1])
            timestamp = d.strftime('%Y-%m-%d %H:%M:%S')
            if d > recentWait:
                cursor = self.db.cursor()
                mySql_insert_query = """INSERT INTO WaitTimes (id, location, department, time, updatedOn, updatedBy, addedOn, addedBy) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """

                
                updatedOn=addedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                updatedBy=addedBy = "OGSS Web Server"
                id = str(uuid.uuid4())
                record = (id, data['location'], data['line'], timestamp, updatedOn, updatedBy, addedOn, addedBy)
                cursor.execute(mySql_insert_query, record)
                self.db.commit()
                print("Record inserted successfully into WaitTime table")

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def upsertRealTimeOilData(self, data, date):
        try:
            cursor = self.db.cursor()
            select = self.selectRealTimeOilSalesOnDate(date)
            if select != None:
                mySql_insert_query = """UPDATE RealTimeOilSales SET grossSales = %s, promotionAmount = %s, updatedOn = %s, updatedBy = %s WHERE id = %s"""
                if data[0] > float(select[2]):
                    updatedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    updatedBy = "OGSS Web Server"
                    record = (data[0], data[1], updatedOn, updatedBy, select[0])
                    cursor.execute(mySql_insert_query, record)
                    self.db.commit()
                    print("Record updated successfully into RealTimeSales table")
                else:
                    print("Real Time Oil record up to date already")
            else:
                mySql_insert_query = """INSERT INTO RealTimeOilSales (id, date, grossSales, promotionAmount, oilMargin, updatedOn, updatedBy, addedOn, addedBy) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """

                updatedOn=addedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                updatedBy=addedBy = "OGSS Web Server"
                oilMargin = self.selectValueFromAppParams('oil')
                id = str(uuid.uuid4())
                record = (id, date, data[0], data[1], oilMargin, updatedOn, updatedBy, addedOn, addedBy)
                cursor.execute(mySql_insert_query, record)
                self.db.commit()
                print("Record inserted successfully into RealTimeSales table")

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def upsertFuelSalesData(self, data, date):
        try:
            cursor = self.db.cursor()
            select = self.selectFuelSalesOnDate(date)
            if select != None:
                mySql_insert_query = """UPDATE FuelSales SET fuelSales = %s, fuelVolume = %s, updatedOn = %s, updatedBy = %s WHERE id = %s"""
                if data[0] > float(select[2]):
                    updatedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    updatedBy = "OGSS Web Server"
                    record = (data[0], data[1], updatedOn, updatedBy, select[0])
                    cursor.execute(mySql_insert_query, record)
                    self.db.commit()
                    print("Record updated successfully into FuelSales table")
                else:
                    print("Fuel Sales record up to date already")
            else:
                yesterdayMargin = self.selectRecentFuelSales()[4]
                mySql_insert_query = """INSERT INTO FuelSales (id, date, fuelSales, fuelVolume, fuelMargin, updatedOn, updatedBy, addedOn, addedBy) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """

                updatedOn=addedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                updatedBy=addedBy = "OGSS Web Server"
                # fuelMargin = self.selectValueFromAppParams('fuel')
                id = str(uuid.uuid4())
                record = (id, date, data[0], data[1], yesterdayMargin, updatedOn, updatedBy, addedOn, addedBy)
                cursor.execute(mySql_insert_query, record)
                self.db.commit()
                print("Record inserted successfully into FuelSales table")

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

            
    def upsertStoreSalesData(self, data, date):
        try:
            cursor = self.db.cursor()
            select = self.selectStoreSalesOnDate(date)
            if select != None:
                mySql_insert_query = """UPDATE StoreSales SET storeSales = %s, updatedOn = %s, updatedBy = %s WHERE id = %s"""
                if (data > float(select[2])):
                    updatedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    updatedBy = "OGSS Web Server"
                    record = (data, updatedOn, updatedBy, select[0])
                    cursor.execute(mySql_insert_query, record)
                    self.db.commit()
                    print("Record updated successfully into StoreSales table")
                else:
                    print("Store Sales record up to date already")
            else:
                recent = self.selectRecentStoreSales()
                mySql_insert_query = """INSERT INTO StoreSales (id, date, storeSales, storeMembers, memberSales, storeMargin, updatedOn, updatedBy, addedOn, addedBy) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

                updatedOn=addedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                updatedBy=addedBy = "OGSS Web Server"
                storeMargin = self.selectValueFromAppParams('store')
                id = str(uuid.uuid4())
                record = (id, date, data, recent[4], 0, storeMargin, updatedOn, updatedBy, addedOn, addedBy)
                cursor.execute(mySql_insert_query, record)
                self.db.commit()
                print("Record inserted successfully into StoreSales table")

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def updateStoreMembersData(self, data, date):
        try:
            cursor = self.db.cursor()
            select = self.selectStoreSalesOnDate(date)
            if select != None:
                mySql_insert_query = """UPDATE StoreSales SET storeMembers = %s, memberSales = %s, updatedOn = %s, updatedBy = %s WHERE id = %s"""
                if (data[1] > float(select[6])):
                    updatedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    updatedBy = "OGSS Web Server"
                    record = (data[0], data[1], updatedOn, updatedBy, select[0])
                    cursor.execute(mySql_insert_query, record)
                    self.db.commit()
                    print("Successfully updated StoreMembers")
                else:
                    print("Store Sales record up to date already")
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def upsertCarwashData(self, data, date):
        try:
            cursor = self.db.cursor()
            select = self.selectWashDataOnDate(date)
            if select != None:
                mySql_insert_query = """UPDATE Carwash SET washMembers = %s, washSales = %s, updatedOn = %s, updatedBy = %s WHERE id = %s"""
                if (data[0] > float(select[2]) or data[1] > float(select[3])):
                    updatedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    updatedBy = "OGSS Web Server"
                    record = (data[0], data[1], updatedOn, updatedBy, select[0])
                    cursor.execute(mySql_insert_query, record)
                    self.db.commit()
                    print("Record updated successfully into Carwash table")
                else:
                    print("Carwash record up to date already")
            else:
                mySql_insert_query = """INSERT INTO Carwash (id, date, washMembers, washSales, washMargin, updatedOn, updatedBy, addedOn, addedBy) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """

                updatedOn=addedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                updatedBy=addedBy = "OGSS Web Server"
                storeMargin = self.selectValueFromAppParams('wash')
                id = str(uuid.uuid4())
                record = (id, date, data[0], data[1], storeMargin, updatedOn, updatedBy, addedOn, addedBy)
                cursor.execute(mySql_insert_query, record)
                self.db.commit()
                print("Record inserted successfully into Carwash table")

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def upsertScorecardData(self, data):
        try:
            cursor = self.db.cursor()
            select = self.selectRecentScorecard()
            date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            if select != None:
                mySql_insert_query = """UPDATE Scorecard SET csaToday = %s, csaMonthly = %s, prodToday = %s, prodMonthly = %s, store1Today = %s, store1Monthly = %s, store2Today = %s, store2Monthly = %s, updatedOn = %s, updatedBy = %s WHERE id = %s"""
                updatedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                updatedBy = "OGSS Web Server"
                record = (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], updatedOn, updatedBy, select[0])
                cursor.execute(mySql_insert_query, record)
                self.db.commit()
                print("Record updated successfully into Scorecard table")
            else:
                mySql_insert_query = """INSERT INTO Scorecard (id, date, csaToday, csaMonthly, prodToday, prodMonthly, store1Today, store1Monthly, store2Today, store2Monthly, updatedOn, updatedBy, addedOn, addedBy) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

                updatedOn=addedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                updatedBy=addedBy = "OGSS Web Server"
                id = str(uuid.uuid4())
                record = (id, date, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], updatedOn, updatedBy, addedOn, addedBy)
                cursor.execute(mySql_insert_query, record)
                self.db.commit()
                print("Record inserted successfully into Scorecard table")

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def insertConnectTeamData(self, data, date):
        try:
            cursor = self.db.cursor()
            mySql_insert_query = """INSERT INTO ConnectTeam (id, date, person, fullTask, action, updatedOn, updatedBy, addedOn, addedBy) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """

            updatedOn=addedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            updatedBy=addedBy = "OGSS Web Server"
            action = data[2][0]+' '+data[2][1]
            id = str(uuid.uuid4())
            record = (id, date, data[0], data[1], action, updatedOn, updatedBy, addedOn, addedBy)
            cursor.execute(mySql_insert_query, record)
            self.db.commit()
            print("Record inserted successfully into ConnectTeam table")

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def insertReviewData(self, data, date):
        try:
            cursor = self.db.cursor()
            mySql_insert_query = """INSERT INTO Reviews (id, date, oilRating, oilCount, gasRating, gasCount, washRating, washCount, updatedOn, updatedBy, addedOn, addedBy) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

            updatedOn=addedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            updatedBy=addedBy = "OGSS Web Server"
            id = str(uuid.uuid4())
            record = (id, date, data['oil']['rating'], data['oil']['count'], data['gas']['rating'], data['gas']['count'], data['wash']['rating'], data['wash']['count'], updatedOn, updatedBy, addedOn, addedBy)
            cursor.execute(mySql_insert_query, record)
            self.db.commit()
            print("Record inserted successfully into Reviews table")

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))


    def insertPayrollData(self, data):
        try:
            cursor = self.db.cursor()
            select = self.selectRecentPayroll()
            lastEndDate = select[2]
            mySql_insert_query = """INSERT INTO Payroll (id, startDate, endDate, amount, addedOn, addedBy, updatedOn, updatedBy) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """

            updatedOn=addedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            updatedBy=addedBy = "OGSS Web Server"
            newStart = lastEndDate + timedelta(days=1)
            newStartDate = newStart.strftime('%Y-%m-%d')
            newEnd = newStart + timedelta(days=13)
            newEndDate = newEnd.strftime('%Y-%m-%d')
            id = str(uuid.uuid4())
            record = (id, newStartDate, newEndDate, data, addedOn, addedBy, updatedOn, updatedBy)
            cursor.execute(mySql_insert_query, record)
            self.db.commit()
            print("Record inserted successfully into Payroll table")

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
    
    def updateFuelSalesGasMargin(self, value):
        try:
            cursor = self.db.cursor()
            now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            select = self.selectFuelSalesOnDate(now)
            if select != None:
                mySql_insert_query = """UPDATE FuelSales SET fuelMargin = %s, updatedOn = %s, updatedBy = %s WHERE id = %s"""
                if float(value) != float(select[4]):
                    updatedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    updatedBy = "OGSS Web Server"
                    record = (float(value), updatedOn, updatedBy, select[0])
                    cursor.execute(mySql_insert_query, record)
                    self.db.commit()
                    print("Record updated successfully into FuelSales table")
                else:
                    print("Fuel Sales record up to date already")
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def updateVendingSales(self, value, date):
        try:
            cursor = self.db.cursor()
            select = self.selectStoreSalesOnDate(date)
            if select != None:
                mySql_insert_query = """UPDATE StoreSales SET vendingSales = %s, updatedOn = %s, updatedBy = %s WHERE id = %s"""
                if float(value) > float(select[5]):
                    updatedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    updatedBy = "OGSS Web Server"
                    record = (float(value), updatedOn, updatedBy, select[0])
                    cursor.execute(mySql_insert_query, record)
                    self.db.commit()
                    print("Record updated successfully into StoreSales table into vending field")
                else:
                    print("Store sales vending record up to date already")
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def updateLotterySales(self, value, date):
        try:
            cursor = self.db.cursor()
            select = self.selectStoreSalesOnDate(date)
            if select != None:
                mySql_insert_query = """UPDATE StoreSales SET lotterySales = %s, updatedOn = %s, updatedBy = %s WHERE id = %s"""
                if float(value) > select[7]:
                    updatedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    updatedBy = "OGSS Web Server"
                    record = (float(value), updatedOn, updatedBy, select[0])
                    cursor.execute(mySql_insert_query, record)
                    self.db.commit()
                    print("Record updated successfully into StoreSales table into lottery field")
                else:
                    print("Store sales lottery record up to date already")
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def updateEmmissionsDone(self, value, date):
        try:
            cursor = self.db.cursor()
            select = self.selectOilSalesOnDate(date)
            if select != None:
                mySql_insert_query = """UPDATE RealTimeOilSales SET emmissionsDone = %s, updatedOn = %s, updatedBy = %s WHERE id = %s"""
                if int(value) > select[4]:
                    updatedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    updatedBy = "OGSS Web Server"
                    record = (int(value), updatedOn, updatedBy, select[0])
                    cursor.execute(mySql_insert_query, record)
                    self.db.commit()
                    print("Record updated successfully into RealTimeOilSales table into emmissionsDone field")
                else:
                    print("RealTimeOilSales emmissions record up to date already")
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def updateVinChecksDone(self, value, date):
        try:
            cursor = self.db.cursor()
            select = self.selectOilSalesOnDate(date)
            if select != None:
                mySql_insert_query = """UPDATE RealTimeOilSales SET vinChecksDone = %s, updatedOn = %s, updatedBy = %s WHERE id = %s"""
                if int(value) > select[5]:
                    updatedOn = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    updatedBy = "OGSS Web Server"
                    record = (int(value), updatedOn, updatedBy, select[0])
                    cursor.execute(mySql_insert_query, record)
                    self.db.commit()
                    print("Record updated successfully into RealTimeOilSales table into vinChecksDone field")
                else:
                    print("RealTimeOilSales vinChecks record up to date already")
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
    
    def selectRealTimeOilSalesOnDate(self, date):
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM RealTimeOilSales WHERE date = %s"""
            d = datetime.strptime(date, "%Y-%m-%d").strftime('%Y-%m-%d')
            queryParams = (d,)
            cursor.execute(mySql_select_query, queryParams)
            result = cursor.fetchone()
            cursor.reset()
            return result
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))
    
    def selectFuelSalesOnDate(self, date):
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM FuelSales WHERE date = %s"""
            d = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d')
            queryParams = (d,)
            cursor.execute(mySql_select_query, queryParams)
            result = cursor.fetchone()
            cursor.reset()
            return result
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))

    def selectOilSalesOnDate(self, date):
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM RealTimeOilSales WHERE date = %s"""
            d = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d')
            queryParams = (d,)
            cursor.execute(mySql_select_query, queryParams)
            result = cursor.fetchone()
            cursor.reset()
            return result
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))
    
    def selectStoreSalesOnDate(self, date):
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM StoreSales WHERE date = %s"""
            d = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d')
            queryParams = (d,)
            cursor.execute(mySql_select_query, queryParams)
            result = cursor.fetchone()
            cursor.reset()
            return result
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))
        
    def selectWashDataOnDate(self, date):
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM Carwash WHERE date = %s"""
            d = datetime.strptime(date, '%Y-%m-%d %H').strftime('%Y-%m-%d')
            queryParams = (d,)
            cursor.execute(mySql_select_query, queryParams)
            result = cursor.fetchone()
            cursor.reset()
            return result
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))

    def selectRecentPayroll(self):
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM Payroll ORDER BY endDate DESC"""
            cursor.execute(mySql_select_query)
            result = cursor.fetchone()
            cursor.reset()
            return result
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))

    def selectRecentFuelSales(self):
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM FuelSales ORDER BY date DESC"""
            cursor.execute(mySql_select_query)
            result = cursor.fetchone()
            cursor.reset()
            return result
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))

    def selectRecentScorecard(self):
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM Scorecard ORDER BY date DESC"""
            cursor.execute(mySql_select_query)
            result = cursor.fetchone()
            cursor.reset()
            return result
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))
    
    def selectRecentStoreSales(self):
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM StoreSales ORDER BY date DESC"""
            cursor.execute(mySql_select_query)
            result = cursor.fetchone()
            cursor.reset()
            return result
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))
    
    def selectRecentWaitTimesForDepartment(self, dept):
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM WaitTimes WHERE department = %s ORDER BY time DESC"""
            queryParams = (dept,)
            cursor.execute(mySql_select_query, queryParams)
            result = cursor.fetchone()
            cursor.reset()
            return result
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))

    def selectValueFromAppParams(self, value):
        d = {'oil': 1, 'wash': 2, 'store': 3, 'fuel': 4}
        ind = d[value]
        try:
            cursor = self.db.cursor()
            mySql_select_query = """SELECT * FROM AppParams"""
            cursor.execute(mySql_select_query)
            result = cursor.fetchone()
            cursor.reset()
            return result[ind]
        except mysql.connector.Error as error:
            print("Failed to select from MySQL table {}".format(error))

    def initDB(self):
        try:
            connection = mysql.connector.connect(host='localhost',
                                                database='OGSS',
                                                user=creds.username,
                                                password=creds.password, buffered=True)
            cursor = connection.cursor()
            print("Succesfully initiated database.")
        except mysql.connector.Error as error:
            print("Failed to connect to database {}".format(error))
        return connection
    
    def closeDB(self):
        if self.db.is_connected():
            self.db.close()
            print("MySQL connection is closed")

def main():
    pass

if __name__ == "__main__":
    main()