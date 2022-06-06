# The Effortless Monthly Expense Calculator
#
# By Clive Bluston
# 2nd June 2022
#
#  Up until now all tools that help you calculate your monthly expenses require you to collect
# and enter them into some sort of expense calculator. This requires a lot of effort and is
# error prone.
# This script extracts the information directly from your bank account transactions.
# It will work well even if you have multiple back accounts, investments and credit cards.
# The only condition is that all your expenses eventually land in your current account. This is
# the case for most people.
#
# The script provides a framework and is used as a base class for bank specific subclasses.
# Banks and languages can be added just by creating a new subclass of TransactionAnalyzer
# Use TransactionAnalyzer_BankDiscountEnglish as a template.
#

# You may need to make the following installs
# python.exe -m pip install --upgrade pip
# pip install pandas
# pip install openpyxl
#
# Generate an Excel file of your transactions as follows:
# 1. Login to Bank in a browser
# 2. Set to English (Hebrew can be supported by adjusted the script)
# 3. Go to your Current Account transactions.
# 4. Select 12 months of transactions using the menu.
# 5. Select Export to Excel using the Export menu.
# 6. Save the file.
# Run as follows in Windows Terminal:
# (You can run it in Windows cmd, but it does not support languages other than English)
# python expenseCalc.py Current Account_29052022_0749.xlsx

# Imports
import pandas as pd
import re
import datetime
import json
from os.path import exists
from re import sub
from decimal import Decimal

class TransactionAnalyzer:
    # Abstract class. You need to create a subclass for each Bank.

    # Return the transaction value from the row.
    # Value may be positive(credit or negative(debit)
    def __extractValue(self, row):
        # There may be a unified credit/debit column or seperate cred and debit columns.
        if self.creditDebitValueColumnName is not None:
            value = row[self.creditDebitValueColumnName]
        else:
            valueStr = row[self.debitValueColumnName]
            if len(valueStr) != 0:
                value = -Decimal(sub(r'[^\d.]', '', row[self.debitValueColumnName]))
            else:
                value = Decimal(sub(r'[^\d.]', '', row[self.creditValueColumnName]))
        return value

    # Manage the configuration file.
    # We ask the user which entries are investment descriptions and store them in a file.
    # We also keep the expenses descriptions in the file, so that we do not ask him again about them.
    # Parameters:
    # dataframe - A pandas dataframe object containing the data to be analyzed.
    def __configure(self, dataframe):

        configFileName = type(self).__name__ + "_config.json"

        if exists(configFileName):
            f = open(configFileName, "r")
            configurationDict = json.load(f)
            f.close()
            self.expensesSet = set(configurationDict["expenses"])
            self.investmentsSet = set(configurationDict["investments"])
        else:
            self.expensesSet = set()
            self.investmentsSet = set()

        askUserSet = set()

            # Iterate over all transactions.
        for index, row in dataframe.iterrows():
            description = row[self.descriptionColumnName]

            # Stop on end of data.
            if type(description) != str or description == " ":
                break

            # Exclude known non-expenses.
            if re.search(self.excludeRegex,description) != None:
                print("Exclude:",description)
                continue

            value = self.__extractValue(row)

            if value < 0:
                if description in self.expensesSet or description in self.investmentsSet:
                    # We know about this already so we can ignore it
                    continue
                else:
                    # We do not know about thgis expense type so we add it to the set.
                    askUserSet.add(description)

        # If we have found some expenses that we need to ask the user about.
        if len(askUserSet) != 0:
                # Ask user if anything here is an investment.
            askUserList = list(askUserSet)
            # Until user hits enter without a number or we exhaust the list.
            index = 1
            while index and len(askUserList) > 0:
                    # Display the list with indexes.
                for item in askUserList:
                    print(askUserList.index(item) + 1, item)

                print("Choose one item that is and investment, otherwise <enter>:",end = " ")
                # Get the users choice.
                index = input()
                # If it was not <enter>
                if index:
                    # Check that input is a single digit.
                    if index.isdigit() and len(index) == 1:
                        index = int(index) - 1
                        description = askUserList[index]
                        # Add it to the investments set
                        self.investmentsSet.add(description)
                        # Do not ask again about this one.
                        askUserList.remove(description)
                        # Ask again
                        index = 1
                    else:
                        print("Enter a single digit or <enter>")

            # Transfer what is left to expensesSet. We will save this so that we will never ask again.
            for expense in askUserList:
                self.expensesSet.add(expense)

            # Prepare a dictionary to save in the json file.
            configurationDict = dict({"expenses" : list(self.expensesSet), "investments" : list(self.investmentsSet)})

            print("Saving configuration file.")
            f = open(configFileName, "w")
            json.dump(configurationDict, f)
            f.close()

    # Analyze the transaction file.
    # Parameters:
    # dataframe - A pandas dataframe object containing the data to be analyzed.
    # nonBankMonthlyExpenses - A list of tuples of the form [ expense description, sum ] with an entry for each non-bank expense.
    def analyze(self, dataframe, nonBankMonthlyExpenses):

        # Read, create or modify configuration, as needed.
        self.__configure(dataframe)

        # Initial values
        sum = 0
        totalMonthlyExpenses = 0
        extraordinary = 0
        income = 0
        months = [0,0,0,0,0,0,0,0,0,0,0,0]
        # Fixed number of Months. A future improvement would be to calculate this from the data.
        numberOfMonths = 12

        # Calculate non bank expenses per month
        for expense in nonBankMonthlyExpenses:
            totalMonthlyExpenses -= expense[1]
        # Now for the whole period
        sum = totalMonthlyExpenses * numberOfMonths

        # Iterate over all transactions
        for index, row in dataframe.iterrows():
            description = row[self.descriptionColumnName]

            # Stop on end of data
            if type(description) != str or description == " ":
                break

            # Exclude known non-expenses and investments
            if re.search(self.excludeRegex,description) != None or description in self.investmentsSet:
                #print("Exclude:",description)
                continue

            value = self.__extractValue(row)

            if value < 0:
                date = row[self.dateColumnName]
                dt = pd.to_datetime(date)
                # Display and collect extrordinary expenses.
                if value < -self.extraordinaryExpenseFloor:
                    extraordinary += value
                    print("Extraordinary expense: ",date," ",description," ",value)
                else:
                    # Accumulate the monthly value.
                    months[dt.month -  1] += value
                # Accumulate the total value
                sum += value
            else:  # Value > 0
                if re.search(self.includeRegex,description) != None:
                    # Accumulate expenses that ere returned to your account.
                    sum += value;
                    #print("Returned expense: ",date," ",description," ",value)
                elif re.search(self.incomeRegex,description) != None:
                    # Accumulate income
                    income += value

        # Output
        print("\nTotal expenses = %d Monthly = %d"%(abs(sum),abs(sum)/numberOfMonths))

        # Print again excluding extraordinary expenses.
        sum = sum - extraordinary

        print("\nExcluding extraordinary expenses:")
        print("Total expenses = %d Monthly= %d"%(abs(sum),abs(sum)/numberOfMonths))

        # Print monthly values. Not very accurate because we may start in the middle of a month,
        # so part of the month maybe from previous year.
        print("\nExpenses by month.")
        for month in range(0,numberOfMonths):
            print("%10s"%datetime.date(1900, month + 1, 1).strftime('%B')," "," - %d"% abs(months[month] + totalMonthlyExpenses))
        # Income
        print("\nTotal salary = %d Monthly = %d."%(abs(income),abs(income)/numberOfMonths))



