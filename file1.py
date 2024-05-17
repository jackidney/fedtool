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
#FOMCdf['FOMCDate'] = pd.to_datetime(FOMCdf['FOMCDate'])

today = datetime.date(2024, 5, 17)

# Takes in the a month and year as numerics and spits out a proper product code of
# ZQ Month Year
def ProductCodeTwoNumbers(month, year):
    my_dict = {
    1: 'F', 2: 'G', 3: 'H', 4: 'J', 5: 'K', 6: 'M', 7: 'N', 8: 'Q', 9: 'U', 10: 'V', 11: 'X', 12: 'Z'
}
    return("ZQ" + my_dict[month] + str(year))


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




    

def main():
    """ Main entry point of the app """
    print("hello world")



if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()