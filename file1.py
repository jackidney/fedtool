#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Jack K"
__version__ = "0.1.0"
__license__ = "MIT"

#import requisite modules
import pandas as pd 
import openpyxl

# Here 0th column will be extracted 
df = pd.read_excel("/Users/jackkidney/Documents/fedwatch/fedtool/data/fomc_data.xlsx", index_col = 0)  


# Takes in the a month and year as numerics and spits out a proper product code of
# ZQ Month Year
def ProductCodeTwoNumbers(month, year):
    my_dict = {
    1: 'F',
    2: 'G',
    3: 'H',
    4: 'J',
    5: 'K',
    6: 'M',
    7: 'N',
    8: 'Q',
    9: 'U',
    10: 'V',
    11: 'X',
    12: 'Z'
}
    return("ZQ" + my_dict[month] + str(year))

# Takes in a current
def NearestMeeting(CurrentDate, prnt=False):
    if not isinstance(CurrentDate, list):
        raise TypeError("Date must be in list = [month, day, year] format")
    if len(CurrentDate) != 3:
        raise ValueError("Date list must have size 3")
    
    pass
    

def main():
    """ Main entry point of the app """
    print("hello world")



if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()