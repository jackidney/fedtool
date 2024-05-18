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

# CASE 1:
# If we ARE currently in an FOMC month, then the nearest upcoming month with no meeting is
    #  next month

#CASE 2:
# If we are NOT currently in an FOMC month, then the nearest upcoming month with no meeting is
    # the month after next month

def NearestNonMeetingMonth(CurrentDate, prnt=False):
    if not isinstance(CurrentDate, datetime.date):
        raise TypeError("CurrentDate must be a datetime object")
    for row in FOMCdf['FOMCDate']:
        # Scenario 1
        if ((row.year == CurrentDate.year) & 
            (row.month == CurrentDate.month)):
            return (CurrentDate+relativedelta(months=1))
        # Scenario 2
    return (CurrentDate+relativedelta(months=2))

def calculate(ReferenceDate = today, NumberOfMeetings = 2):
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
    print(row, saved_index)
    # Now get a list of the rows in FOMCdf['FOMCDate'] for saved_index to saved_index-NumberOfMeetings
    rows_list = FOMCdf['FOMCDate'].iloc[(saved_index - NumberOfMeetings + 1):saved_index + 1].tolist()
    print(rows_list)
    print(max(rows_list))

    position = datetime.date(today.year, today.month, 1)
    lst = list()
    while(position < max(rows_list)):
        lst.append(position)
        print(position)
        position = position+relativedelta(months=1)
        print(position)

    # REAL DEAL
    for current in lst:
        for _ in range(3):
                date = current
                start = 1 if _ == 0 else 0
                average = 1 if _ == 1 else 0
                end = 1 if _ == 2 else 0
            
                data = data.append({'Date': date, 'START': start, 'AVERAGE': average, 'END': end}, ignore_index=True)
    print(data)

    uniques = data['Date'].unique()

    print(contracts)

    for iteration in uniques:
        #print(ProductCodeTwoNumbers(iteration.month, iteration.year))
        val = contracts.loc[contracts['CONTRACT'] == ProductCodeTwoNumbers(iteration.month, iteration.year), 'LAST'].values[0]
        print(val)
        data.loc[((data['Date'] == iteration) & (data['AVERAGE'] == 1)), "Price"] = val
    
    print(data)

    


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