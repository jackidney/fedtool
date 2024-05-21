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
#FOMCdf['FOMCDate'] = pd.to_datetime(FOMCdf['FOMCDate'])

today = datetime.date(2024, 5, 17)

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

    def FFEREnd(date = datetime.date(2024, 9, 1)):
        #Avg. FFER
        AVGFFER = data.iloc(data['Date'] == date)
        print(AVGFFER)
        
        value = data.iloc(data['Date'] == date)
        data.iloc[(data['Date'] == date) & (data['END'] == 1), "Price"] = value
        pass
        
    FFEREnd()
    print(data)

    #FFER End = [ (Avg. FFER) - (% days before meet.)*(FFER Start) ] / (% days after meet.)
    #FFEREnd = [ data['Date']data['Date']


    # loop = (data['Date'].values)
    # for item in loop:
    #     pass
#data['Date' == item AND 
        
    
def FillDays(frame):
     
    pass   
        

    #for current in lst:
    

def main():
    """ Main entry point of the app """
    print("hello world")
    calculate()


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()