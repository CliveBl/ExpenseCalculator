# Generate an Excel file of your transactions as follows:
# 1. Login to Bank in a browser
# 3. Go to your Current Account transactions.
# 4. Select 12 months of transactions using the menu.
# 5. Select Export to Excel using the Export menu.
# 6. Save the file.
# Run as follows in Windows Terminal:
# (You can run it in Windows cmd, but it does not support languages other than English)
# python bankDiscountHebrew.py "עובר ושב_12062022_1710.xlsx"

from expenseCalc import TransactionAnalyzer
import sys
import re
import pandas as pd
import os
import webbrowser

class TransactionAnalyzer_BankDiscountHebrew(TransactionAnalyzer):
    # This a bank/language specific subclass. Use it as a template for a new bank or language.
    def __init__(self):
 
        self.bankName = "Bank Discount"
        self.currency = "Shekels"

        # Excel column names
        self.dateColumnName = "יום ערך"
        self.creditDebitValueColumnName = "₪ זכות/חובה "
        self.debitValueColumnName = None
        self.creditValueColumnName = None
        # There can only be a single description column, so if there are more in the data they must be combined.
        self.descriptionColumnName = "תיאור התנועה"
        # format argument of pandas.to_datetime
        self.dateFormat = None

        # Transfers to my accounts and investment costs:
        # Purchase of shares
        # Savings account
        # Savings account
        # Savings account
        # Tax on savings
        # Tax on savings
        # Tax on savings
        # Tax on savings
        self.excludeRegex = \
                            "מכירת ניע.*" + "|" + \
                            "קניית ני.*" + "|" + \
                            "הפקדה לפיקדון נזיל יומי+" + "|" + \
                            "הפקדה לפיקדון פקדון נזיל יומי" + "|" +\
                            "משיכה מפיקדון נזיל חודשי" + "|" + \
                            "הפקדה לפיקדון נזיל חודשי" +"|" + \
                            "תשלום מס על רווח מפיקדון" + "|" + \
                            "חידוש פיקדון פר יום" + "|" + \
                            "החזר מס מניירות ערך" + "|" +\
                            "ניכוי מס מניירות ערך" + "|" +\
                            "חיוב מס בפרעון פיקדון" + "|" +\
                            "תשלום מס במקור"

        # Expenses that were returned to me via BIT(like Venmo). We assume that anything coming from BIT is the return of an expense.
        # It could also be other things like the sale of a personal item, however that can also be considered a negative expense.
        self.includeRegex = ".*799-0095-000000000.*"

        # Everything here is income (Salary etc.)
        self.incomeRegex = "משכורת.*" + "|" +\
                           "מיטב דש טר" + "|" +\
                           "פוינטר טלו"
        
        # Anything equal to and above this is an extraordinary expense.
        # We show results that both exclude and include extraordinary expenses.
        self.extraordinaryExpenseFloor = 10000

    # Return a DatFrame or None if the file could not be identified for this class.
    def getDataFrame(fileName):
        # Try to identify the bank/language according to the name of the file.
        # If not, we could look inside the file.
        if re.search("ובר ושב.*_....\.xlsx",fileName):
                # Load spreadsheet
            xl = pd.ExcelFile(fileName)

            #print(xl.sheet_names)

            # First row is the title row of the sheet. It is 9 (Which is 8 when zero based)
            firstRow = 8
            # Load a sheet into a DataFrame by name: df1. First row is 9 (Which is 8 when zero based)
            dataframe = xl.parse("עובר ושב", header=firstRow)
            return dataframe
        else:
            return None


# Main
# Check arguments
if len(sys.argv) != 2:
    print("Please specify an xlsx file with 12 months of transactions on the command line.")
    exit()

# First argument is the Spreadsheet filename. Ignore the rest.
fileName = sys.argv[1]

# Customize these
# These are expenses that are paid directly out of your salary and do not go through any bank account or credit card.
nonBankMonthlyExpenses = [\
                          ["Company meal card",500],\
                          ["Company car",0],\
                          ["Company medical insurance",0]\
                         ]

df = TransactionAnalyzer_BankDiscountHebrew.getDataFrame(fileName)
if df is not None:
    t = TransactionAnalyzer_BankDiscountHebrew()
    t.analyze(df, nonBankMonthlyExpenses)
    t.renderConsole()
    htmlFile = os.path.splitext(fileName)[0] + ".html"
    t.renderHTML(htmlFile)
    #webbrowser.open(os.path.join('file://', htmlFile))
else:
    print("The bank could not be identified from the file: ",fileName)



    
	