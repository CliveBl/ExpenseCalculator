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

# You may need to make the following installs:
# python.exe -m pip install --upgrade pip
# pip install pandas
# pip install openpyxl
# pip install matplotlib
#

# Imports
import pandas as pd
import matplotlib.pyplot as plt
import re
import datetime
from datetime import date
import time
import json
from os.path import exists
from re import sub
from decimal import Decimal
from parse import parse

class TransactionAnalyzer:
    # Abstract class. You need to create a subclass for each Bank.

    def renderConsole(self):
        if not hasattr(self, "outputList"):
            print("Please call analyze() first")
            return
            
        # Render MD format to console.
        widthFormat = "{:^50}"
        for item in self.outputList:
            if item[:2] == "##":
                # level 2 header
                print("")
                print(widthFormat.format(item[2:]))
                print(widthFormat.format(len(item[2:])*"-"))
            elif item[:1] == "#":
                # Level 1 header
                print("")
                print(widthFormat.format(item[1:]))
                print(widthFormat.format(len(item[1:])*"-"))
            elif item[:2] == "![":
                # Image
                image = parse("![Plot saved to:]({imageFileName})",item)
                print("")
                # If we are not in test mode.
                if not self.testmode:
                    plt.imread(image["imageFileName"])
                    # Display it later
            else:
                # Normal text
                 print(item)
                 
        # Show the chart at the end so that all the console text is shown first.
        # (A batch file can create this file in order not to stop and display the plot.)
        if not self.testmode:
            # Display it.
            plt.show()
                
                
    # Render MD format to HTML.
    def renderHTML(self, htmlFileName):
    
        def openParagraph():
           nonlocal paragraphOpen
           if not paragraphOpen:
                # Open paragraph
                html.write("<p>")
                paragraphOpen = True

        def closeParagraph():
            nonlocal paragraphOpen
            if paragraphOpen:
                # Close paragraph
                html.write("</p>")
                paragraphOpen = False

        if not hasattr(self, "outputList"):
            print("Please call analyze() first")
            return
            
        html = open(htmlFileName, "w",encoding = "utf-8")
        
        html.write("<!DOCTYPE html>\n<html><head><meta charset=\"UTF-8\"><style>  p{ font-family: 'Courier New', monospace;}")
        html.write("</style></head><body>")
        
        paragraphOpen = False
        
        for item in self.outputList:
            if item[:2] == "##":
                # level 2 header
                closeParagraph()
                html.write("<h2>{}</h2>".format(item[2:]))
            elif item[:1] == "#":
                # Level 1 header
                closeParagraph()
                html.write("<h1>{}</h1>".format(item[1:]))
            elif item[:2] == "![":
                # Image
                closeParagraph()
                r = parse("![Plot saved to:]({imageFileName})",item)
                html.write("<img src={} >".format(r["imageFileName"]))
            else:
                # Normal text
                openParagraph()
                # Replace spaces with nbsp in order to retain table format.
                html.write("{}<br>\n".format(item.replace(" ","&nbsp;")))
                
        closeParagraph()
            
        html.write("</body></html>")
        html.close()

    # Return the transaction value from the row as a float.
    # Value may be positive(credit) or negative(debit)
    def __extractValue(self, row):
        # There may be a unified credit/debit column or seperate cred and debit columns.
        if self.creditDebitValueColumnName is not None:
            value = row[self.creditDebitValueColumnName]
        elif self.debitValueColumnName is not None and self.creditValueColumnName is not None:
            # Check if there is a value in debitValueColumnName
            valueStr = row[self.debitValueColumnName]
            if type(valueStr) == float and valueStr != 0.0:
                value = -valueStr
            else:
                if type(valueStr) == str and len(valueStr) != 0:
                    value = -Decimal(sub(r'[^\d.]', '', valueStr))
                else:
                    # Check if there is a value in creditValueColumnName
                    valueStr = row[self.creditValueColumnName]
                    if type(valueStr) == float:
                        value = valueStr
                    else:
                        value = Decimal(sub(r'[^\d.]', '', valueStr))
        else:
            print("Either self.creditDebitValueColumnName or self.debitValueColumnName and self.creditValueColumnName must not be None")
            
        return float(value)

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
            self.dateOfBirth = configurationDict["dateOfBirth"]
        else:
            self.expensesSet = set()
            self.investmentsSet = set()
            self.dateOfBirth = ""
            
        congigurationChanged = False

            
        # Get date of birth
        if len(self.dateOfBirth) == 0 and not self.testmode:
            self.dateOfBirth = input("Enter your date of birth so that we can make FIRE calculations (dd/mm/yyyy): ")
            try:
                # Check for valid input.
                valid_date = time.strptime(self.dateOfBirth, '%d/%m/%Y')
                congigurationChanged = True
            except ValueError:
                print("Invalid date. Remove {} to try again.".format(configFileName))
                self.dateOfBirth = ""
        
        # Create an empty set.
        askUserSet = set()
        # Iterate over all transactions in order to gather expense types that we do not know about.
        for index, row in dataframe.iterrows():
            description = row[self.descriptionColumnName]

            # Stop on end of data.
            if type(description) != str or description == " ":
                break

            # Exclude known non-expenses.
            if re.search(self.excludeRegex,description) != None:
                #print("Exclude:",description)
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
            # Ask the user if anything here is an investment.
            askUserList = list(askUserSet)
            # Until user hits enter without a number or we exhaust the list.
            menuItem = 1
            while menuItem and len(askUserList) > 0:
                # Display the list with indexes.
                for item in askUserList:
                    print(askUserList.index(item) + 1, item)

                print("Choose one item that is an investment, otherwise <enter>:",end = " ")
                # If file does not exist.
                # (A batch file can create this file in order not to wait for input.)
                if not self.testmode:
                    # Get the users choice.
                    menuItem = input()
                else:
                    menuItem = None
                    
                # If it was <enter>
                if not menuItem:
                    # Stop asking
                    break
                    
                # Check that input is a single digit.
                if menuItem.isdigit() and len(menuItem) != 0:
                    menuItem = int(menuItem) - 1
                    # Check range
                    if 0 <= menuItem  <= len(askUserList):
                        description = askUserList[menuItem]
                        # Add it to the investments set
                        self.investmentsSet.add(description)
                        # Do not ask again about this one.
                        askUserList.remove(description)
                        # Ask again
                        menuItem = 1
                        continue
                # Incorrect input
                print("Enter a menu item or <enter>")

            # Transfer what is left to expensesSet. We will save this so that we will never ask again.
            for expense in askUserList:
                self.expensesSet.add(expense)
                
            congigurationChanged = True

        if congigurationChanged:
            # Prepare a dictionary to save in the json file.
            configurationDict = dict({"expenses" : list(self.expensesSet),
                                      "investments" : list(self.investmentsSet),
                                      "dateOfBirth" : self.dateOfBirth
                                      })

            print("Saving configuration file to ",configFileName)
            f = open(configFileName, "w")
            json.dump(configurationDict, f)
            f.close()

    # Analyze the transaction file.
    # Function will block unless a file "testmode.tmp" is present.
    # Parameters:
    # dataframe - A pandas dataframe object containing the data to be analyzed. 
    # Assumptions: The transactions are from newest to oldest.
    #              There is only a single description column.
    # nonBankMonthlyExpenses - A list of tuples of the form [ expense description, sum ] with an entry for each non-bank expense.
    # plotFileName - The name of a file to output the plot to.
    def analyze(self, dataframe, nonBankMonthlyExpenses = None):

        # Check if we are in test mode by the existence of the file.
        self.testmode = exists("testmode.tmp")

        # Read, create or modify configuration, as needed.
        self.__configure(dataframe)

        # Initial values
        sum = 0
        totalMonthlyNonBankExpenses = 0
        extraordinary = 0
        income = 0
        expensesPerMonth = [0,0,0,0,0,0,0,0,0,0,0,0]
        salaryPerMonth = [0,0,0,0,0,0,0,0,0,0,0,0]
        # Fixed number of Months. A future improvement would be to calculate this from the data.
        numberOfMonths = 12
        lastDate = " "
        # Generate Output to a list in MD format.
        self.outputList = []

        if nonBankMonthlyExpenses:
            # Calculate non bank expenses per month
            for expense in nonBankMonthlyExpenses:
                totalMonthlyNonBankExpenses -= expense[1]
            # Now for the whole period
            sum = totalMonthlyNonBankExpenses * numberOfMonths

        # Iterate over all transactions
        for index, row in dataframe.iterrows():
            description = row[self.descriptionColumnName]

            # Stop on end of data
            if type(description) != str or description == " ":
                # Break out of for.
                break
                
            # Just in case there is a dirty date value we convert it to datetime.
            # Specifying self.dateFormat can fix an erroneos conversion.
            lastDate = pd.to_datetime(row[self.dateColumnName],format=self.dateFormat)
            #print(lastDate,"   ",row.name,"  ", row[self.dateColumnName],"   ",index)

            # On the first row record the date. This is the latest.
            if index == 0:
                endDate = lastDate

            # Exclude known non-expenses and investments
            if re.search(self.excludeRegex,description) != None or description in self.investmentsSet:
                #print("Exclude:",description)
                continue

            # Get the value.
            value = self.__extractValue(row)

            dt = pd.to_datetime(lastDate)
            if value < 0:
                # Display and collect extrordinary expenses.
                if value < -self.extraordinaryExpenseFloor:
                    extraordinary += value
                    self.outputList.append("Extraordinary expense: {} {} {}".format(lastDate,description,value))
                else:
                    # Accumulate the monthly expenses.
                    expensesPerMonth[dt.month -  1] -= value
                # Accumulate the total expenses
                sum += value
            else:  # Value > 0
                if re.search(self.includeRegex,description) != None:
                    # Accumulate expenses that ere returned to your account.
                    sum += value;
                    #print("Returned expense: ",date," ",description," ",value)
                elif re.search(self.incomeRegex,description) != None:
                    # Accumulate income
                    income += value
                    salaryPerMonth[dt.month -  1] += value

        # On the last row, record the date. This is the oldest.
        startDate = lastDate
                
        monthNames =  'January', 'February', 'March','April','May','June','July','August','September','October','November','December'

        titleText = self.bankName + " from: " + startDate.strftime("%d/%m/%Y") + " to: " + endDate.strftime("%d/%m/%Y")

        # Formatting function for currency values.
        currency = lambda value: "{:,.2f}".format(value)
        
        series = lambda sum, inflation, years: abs(sum)*(1-inflation**(years+1))/(1 - inflation)
        
        self.outputList.append("#" + titleText)
        self.outputList.append("##Expense Summary")
        self.outputList.append("Including extraordinary expenses:")
        toatlExpenseText = "Total expenses = {} Monthly= {}".format(currency(abs(sum)),currency(abs(sum)/numberOfMonths))
        self.outputList.append(toatlExpenseText)

        # Print again excluding extraordinary expenses.
        sum = sum - extraordinary
        averageMonthly = abs(sum)/numberOfMonths

        self.outputList.append("Excluding extraordinary expenses:")
        expenseText = "Total expenses = {} Monthly= {}".format(currency(abs(sum)),currency(averageMonthly))
        self.outputList.append(expenseText)

        # Print monthly values. 
        # Note that our data may start in the middle of a month,
        # so one of the months may be partly from this year and partly from last year.
        self.outputList.append("##Monthly Summary")
        self.outputList.append("      Month      Expenses      Income      Profit/Loss")
        profit = 0
        for month in range(0,numberOfMonths):
            # Expenses include totalMonthlyNonBankExpenses, but they are not used in Profit/Loss calculation
            # because they are already part of the salary.
            self.outputList.append("{:>10}".format(datetime.date(1900, month + 1, 1).strftime('%B')) +\
            "  - {:>10}".format(currency(abs(expensesPerMonth[month] - totalMonthlyNonBankExpenses))) +\
            "   {:>10}".format(currency(salaryPerMonth[month])) +\
            "   {:>10}".format(currency(salaryPerMonth[month] - abs(expensesPerMonth[month])))\
            )
            profit += salaryPerMonth[month] - abs(expensesPerMonth[month])

        self.outputList.append("=====================================================")
        self.outputList.append("Total          {:>10}".format(currency(abs(sum))) + "   {:>10}".format(currency(income)) +"   {:>10}".format(currency(profit)))
        self.outputList.append("=====================================================")
            
        # Income
        self.outputList.append("##Income Summary")
        monthlySalary = income/numberOfMonths
        salaryText = "Total income = {} Monthly = {}".format(currency(abs(income)),currency(monthlySalary))
        self.outputList.append(salaryText)


        # Bar chart output.
        # Put all the information on a bar chart
        data = {
            'Expenses': [],
            'Salary':[]
        }
        for month in range(0,numberOfMonths):
            data['Expenses'].append(abs(expensesPerMonth[month] - totalMonthlyNonBankExpenses))
            data['Salary'].append(salaryPerMonth[month])
            
        monthlydf = pd.DataFrame(data, index=monthNames)
        
        # Create a title with a summary of all the information gathered.
        plotTitle = titleText  + "\n" +\
                    salaryText + "\n" +\
                    expenseText
        # Create the chart.
        ax = monthlydf.plot.barh(title=plotTitle, stacked=False, grid=True, color = {"Expenses" :"red","Salary":"green"})
        # Label the axis.
        ax.set_xlabel(self.currency)
        ax.set_ylabel("Month")
        
        # Create plot file name.
        plotFileName = type(self).__name__ + ".png"
            
        plt.savefig(fname = plotFileName, bbox_inches = "tight")
        self.outputList.append("![Plot saved to:]({})".format(plotFileName))
                    
        # F.I.R.E
        self.outputList.append("#F.I.R.E Summary")
        
        # Calculate age from date of birth
        if len(self.dateOfBirth) != 0:
            age = date.today().year - time.strptime(self.dateOfBirth, '%d/%m/%Y').tm_year
        else:
            age = 60
           
        if income > 0.0:
            self.outputList.append("You are saving {:.0%} of your income.".format(1-abs(sum/income)))
        else:
            self.outputList.append("You have no income.")
            
        inflation = 4.0
        years = 0
        self.outputList.append("##How much you will need until you start taking your pension")
        self.outputList.append("Assumed inflation: {}  Current age: {}".format(inflation, age))
        self.outputList.append("")
        self.outputList.append("Pension Age   Savings Required      Required Net Pension")
        self.outputList.append("               (Until pension)         (After tax)")
        for age in range(age,71):
            self.outputList.append(str(age) +\
                  "   {:>20}".format(currency(series(sum,1 + inflation/100, years)))+\
                  "   {:>20}".format(currency(abs(sum)*(1+ inflation/100)**years/12))\
                  )
            years += 1



