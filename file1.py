#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Jack K"
__version__ = "0.1.0"
__license__ = "MIT"

#import requisite modules
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import calendar
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# import fomc data as a list
FOMCdf = pd.read_excel("/Users/jackkidney/Documents/fedwatch/fedtool/data/fomc_data.xlsx", index_col = None)
contracts = pd.read_excel("/Users/jackkidney/Documents/fedwatch/fedtool/data/contracts.xlsx", index_col = None) 

today = datetime.date(2024, 5, 17)
NumberOfMeetings = 5

# Takes in the a month and year as numerics and spits out a proper product code of
# ZQ Month Year
def ProductCodeTwoNumbers(month, year):
    my_dict = {
    1: 'F', 2: 'G', 3: 'H', 4: 'J', 5: 'K', 6: 'M', 7: 'N', 8: 'Q', 9: 'U', 10: 'V', 11: 'X', 12: 'Z'
}
    return("ZQ" + my_dict[month] + str(year)[-2:])


# NearestNonMeetingMonth takes in a current date and finds the nearest upcoming month with no FOMC meeting


#https://stackoverflow.com/questions/13703720/converting-between-datetime-timestamp-and-datetime64

def toDT(input):
    unix_epoch = np.datetime64(0, 's')
    one_second = np.timedelta64(1, 's')
    seconds_since_epoch = (input - unix_epoch) / one_second
    return(datetime.datetime.utcfromtimestamp(seconds_since_epoch).date())

def NearestNonMeetingMonth2(CurrentDate = today, length = 8):
    frame = FOMCdf['FOMCDate']
    frame = frame.apply(toDT)
    list1 = frame[frame > CurrentDate]
    list1 = list1.apply(lambda x: x.replace(day=1))

    sdate = datetime.date(CurrentDate.year, CurrentDate.month + 1, 1)
    list2 = pd.date_range(sdate, periods = length, freq='MS')

    output = pd.Series(list2).loc[~pd.Series(list2).isin(list1)].min()
    output = output.to_pydatetime()
    return(output)


# def NearestNonMeetingMonth2(CurrentDate = today, length = 8):
#     frame = FOMCdf['FOMCDate']
#     frame['FOMCDate'] = frame['FOMCDate'].apply(toDT)
#     list1 = frame[frame['FOMCDate'] > today]['FOMCDate']
#     list1 = list1.apply(lambda x: x.replace(day=1))

#     sdate = datetime.date(CurrentDate.year, CurrentDate.month + 1, 1)
#     list2 = pd.date_range(sdate, periods = length, freq='MS')

#     output = pd.Series(list2).loc[~pd.Series(list2).isin(list1)].min()
#     output = output.to_pydatetime()
#     return(output)


def calculate(ReferenceDate = today, NumberOfMeetings = 5):
    data = pd.DataFrame(columns=[
    'Date',
    'START',
    'AVERAGE',
    'END',
    'Days',
    '% Days',
    'Price',
    'Implied Rate',
    'Monthly Change',
    '# of 25bp Hikes',
    '# Hikes Breakdown'])

    # Iterate over the rows of FOMCdf['FOMCDate'] and find the least row where FOMCDate is greater than or equal to ReferenceDate
    saved = datetime.date(2050, 3, 3)
    saved_index = None  
    
    for index, row in FOMCdf['FOMCDate'].iteritems():
        if (row >= ReferenceDate) and (row < saved):
            saved = row
            saved_index = index
    # Now get a list of the rows in FOMCdf['FOMCDate'] for saved_index to saved_index-NumberOfMeetings
    rows_list = FOMCdf['FOMCDate'].iloc[(saved_index - NumberOfMeetings + 1):saved_index + 1].tolist()

    position = datetime.date(today.year, today.month, 1)
    lst = list()
    while(position < max(rows_list)):
        lst.append(position)
        position = position+relativedelta(months=1)

    # REAL DEAL
    for current in lst:
        for _ in range(3):
                date = current
                start = 1 if _ == 0 else 0
                average = 1 if _ == 1 else 0
                end = 1 if _ == 2 else 0
                data = data.append({'Date': date, 'START': start, 'AVERAGE': average, 'END': end}, ignore_index=True)
    uniques = data['Date'].unique()

    #print(contracts)

    for iteration in uniques:
        val = contracts.loc[contracts['CONTRACT'] == ProductCodeTwoNumbers(iteration.month, iteration.year), 'LAST'].values[0]
        data.loc[((data['Date'] == iteration) & (data['AVERAGE'] == 1)), "Price"] = val
    
    # Now add day and % values
    # rows_list contains list of relevant FOMC meetings.
    # last day includes that day. ie. if the month ends on march 31st and the meeting takes place on march 31st, then number of days in End is 0.
    for row in rows_list:
        start_days = (row.day)
        end_days = (calendar.monthrange(row.year, row.month)[1] - row.day)

        row_sterilized = datetime.date(row.year, row.month, 1)

        data.loc[((data['Date'] == row_sterilized) & (data['START'] == 1)), "Days"] = start_days
        data.loc[((data['Date'] == row_sterilized) & (data['END'] == 1)), "Days"] = end_days

        data.loc[((data['Date'] == row_sterilized) & (data['START'] == 1)), "% Days"] = (start_days / calendar.monthrange(row.year, row.month)[1])
        data.loc[((data['Date'] == row_sterilized) & (data['END'] == 1)), "% Days"] = (end_days / calendar.monthrange(row.year, row.month)[1])
    
    BasePosition = datetime.date(NearestNonMeetingMonth2(today).year, NearestNonMeetingMonth2(today).month, 1)


    # Extract Base Node Price, save.
    BasePrice = data.loc[(data['Date'] == BasePosition) & (data['AVERAGE'] == 1), "Price"]

    data.loc[((data['Date'] == BasePosition + relativedelta(months=1)) & (data['START'] == 1)), "Price"] = BasePrice.values[0]
    data.loc[((data['Date'] == BasePosition - relativedelta(months=1)) & (data['END'] == 1)), "Price"] = BasePrice.values[0]
    
    print(data)
    return(data)

def BackFill(center, data):
   
    # Make center month fill in
    AVG = data.loc[((data['Date'] == center) & (data["AVERAGE"] == 1)), "Price"].values[0]
    print(AVG)
    # Set month end and month start price to average, since rate shouldn't 
    # change at all from average during a non-meeting month
    data.loc[((data['Date'] == center) & (data["START"] == 1)), "Price"] = AVG
    data.loc[((data['Date'] == center) & (data["END"] == 1)), "Price"] = AVG


    loop = data["Date"].values
    previous = center

    while True:
        current = previous - relativedelta(months=1)
        if current not in loop:
            break
        if current in loop:
            print("current:", current)
            print("previous:", previous)
            print(pd.isna(data.loc[((data['Date'] == previous) & (data["END"] == 1)), "% Days"].values[0]))
            

            if pd.isna(data.loc[((data['Date'] == current) & (data["END"] == 1)), "% Days"].values[0]):
                print("current month ", current, " is a non-meeting month")
                # Find the month's average
                AVG = data.loc[((data['Date'] == current) & (data["AVERAGE"] == 1)), "Price"].values[0]
                print(AVG)
                # Set month end and month start price to average, since rate shouldn't 
                # change at all from average during a non-meeting month
                data.loc[((data['Date'] == current) & (data["START"] == 1)), "Price"] = AVG
                data.loc[((data['Date'] == current) & (data["END"] == 1)), "Price"] = AVG
            

            #NEW LOGIC: If current month is a fed meeting month.
                # Fill in the month end with the next month's beginning.
                # Then run FFStart to get the FF at the start of the month using the Average and month end FF
            if not(pd.isna(data.loc[((data['Date'] == current) & (data["END"] == 1)), "% Days"].values[0])):
                print("Current month", current, " is a meeting month")
                #Set current month's FFend to previous month's FF start
                previous_month_FFstart = data.loc[(data['Date'] == previous) & (data["START"] == 1), "Price"].values[0]
                print(previous_month_FFstart)
                data.loc[((data['Date'] == current) & (data["END"] == 1)), "Price"] = previous_month_FFstart

                #Now run FFstart to calculate the month's beginning using the formula
                FFstart(current, data)
            
        previous = previous - relativedelta(months=1)
        print(data)

def FrontFill(center, data):

    loop = data["Date"].values
    previous = center

    while True:
        current = previous + relativedelta(months=1)
        if current not in loop:
            break
        if current in loop:
            print("current:", current)
            print("previous:", previous)

            # If current month is a non-meeting month, then fill in the month end and month start with month average
            if pd.isna(data.loc[((data['Date'] == current) & (data["END"] == 1)), "% Days"].values[0]):
                print("current month ", current, " is a non-meeting month")
                # Find the month's average
                AVG = data.loc[((data['Date'] == current) & (data["AVERAGE"] == 1)), "Price"].values[0]
                print(AVG)
                # Set month end and month start price to average, since rate shouldn't 
                # change at all from average during a non-meeting month
                data.loc[((data['Date'] == current) & (data["START"] == 1)), "Price"] = AVG
                data.loc[((data['Date'] == current) & (data["END"] == 1)), "Price"] = AVG
            

            #NEW LOGIC: If current month is a fed meeting month.
                # Fill in the current month start with the last month's end.
                # Then run FFend to get the FF at the end of the month using the Average and month start FF
            if not(pd.isna(data.loc[((data['Date'] == current) & (data["END"] == 1)), "% Days"].values[0])):
                print("Current month", current, " is a meeting month")
                #Set current month's FFend to previous month's FF start
                previous_month_FFend = data.loc[(data['Date'] == previous) & (data["END"] == 1), "Price"].values[0]
                print(previous_month_FFend)
                data.loc[((data['Date'] == current) & (data["START"] == 1)), "Price"] = previous_month_FFend

                #Now run FFstart to calculate the month's beginning using the formula
                FFend(current, data)
            
        previous = previous + relativedelta(months=1)
        print(data)
    #now change previous month for next loop iteration 
        
    
#FFER End = [ (Avg. FFER) - (% days before meet.)*(FFER Start) ] / (% days after meet.)
def FFend(date, data):
    # If it IS a meeting month, then the following should run
    if (not(pd.isna(data.loc[(data['Date'] == date) & (data['START'] == 1), "% Days"].values))):
        #Avg. FFER
        FFavg = data.loc[(data['Date'] == date) & (data['AVERAGE'] == 1), "Price"].values
        # %before
        pbefore = data.loc[(data['Date'] == date) & (data['START'] == 1), "% Days"].values
        # FF Start
        FFstart = data.loc[(data['Date'] == date) & (data['START'] == 1), "Price"].values
        # %after
        pafter = data.loc[(data['Date'] == date) & (data['END'] == 1), "% Days"].values
            #FFER End = [ (Avg. FFER) - (% days before meet.)*(FFER Start) ] / (% days after meet.)
        result = (FFavg - (pbefore * FFstart)) /  pafter
        data.loc[(data['Date'] == date) & (data['END'] == 1), "Price"] = result
        print(FFavg, pbefore, FFstart, pafter)
    
    # Check if it is NOT a meeting month. If NOT a meeting month then TRUE, and the following statement should run.
    if pd.isna(data.loc[(data['Date'] == date) & (data['START'] == 1), "% Days"].values):
        raise("Meeting month error in call on FFend for " + date)
    pass

#FFER Start = [ (Avg FFER) - (% days after meet.)*(FFER End) ] / (% days before meet.)
def FFstart(date, data):
    # If it IS a meeting month, then the following should run
    if (not(pd.isna(data.loc[(data['Date'] == date) & (data['END'] == 1), "% Days"].values))):
        #Avg. FFER
        FFavg = data.loc[(data['Date'] == date) & (data['AVERAGE'] == 1), "Price"].values
        # %after
        pafter = data.loc[(data['Date'] == date) & (data['END'] == 1), "% Days"].values
        # FF end
        FFend = data.loc[(data['Date'] == date) & (data['END'] == 1), "Price"].values
        # %before
        pbefore = data.loc[(data['Date'] == date) & (data['START'] == 1), "% Days"].values
        #FFER Start = [ (Avg FFER) - (% days after meet.)*(FFER End) ] / (% days before meet.)
        result = (FFavg - (pafter * FFend)) /  pbefore
        data.loc[(data['Date'] == date) & (data['START'] == 1), "Price"] = result
        print(FFavg, pbefore, FFstart, pafter)
    
    # Check if it is NOT a meeting month. If NOT a meeting month then TRUE, and the following statement should run.
    if pd.isna(data.loc[(data['Date'] == date) & (data['END'] == 1), "% Days"].values):
        raise("Meeting month error in call on FFstart for " + date)
    pass
    
def polish(data):
    data['Implied Rate'] = 100 - data['Price']
    loop = data["Date"].values
    for month in loop:
        difference = data.loc[(data['Date'] == month) & (data['END'] == 1), "Implied Rate"].values[0] - data.loc[(data['Date'] == month) & (data['START'] == 1), "Implied Rate"].values[0]
        data.loc[(data['Date'] == month) & (data['END'] == 1), "Monthly Change"] = difference
    data['# of 25bp Hikes'] = data['Monthly Change'].apply(lambda x: (x/.25) if pd.notna(x) else np.nan)
    data['# Hikes Breakdown'] = data['# of 25bp Hikes'].apply(lambda x: (int(x), x - int(x)) if pd.notna(x) else np.nan)

    print(data)

def Generate(data):
    import numpy as np

    # Define the number of rows and columns
    rows, cols = 6, 10

    # Create the array with zeros
    array = np.zeros((rows, cols))

    # Set the first row with incremented values starting from 0, increasing by 0.25
    array[0] = np.arange(0, cols * 0.25, 0.25)

    print(array)
    




    


def main():
    """ Main entry point of the app """
    print("hello world")
    data = calculate()
    BackFill(NearestNonMeetingMonth2(today).date(), data)
    FrontFill(NearestNonMeetingMonth2(today).date(), data)
    polish(data)
    Generate(data)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()