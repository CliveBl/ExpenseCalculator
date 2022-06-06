from expenseCalc import TransactionAnalyzer
import sys
import re
import pandas as pd

class TransactionAnalyzer_BankDiscountEnglish(TransactionAnalyzer):
    # This a bank/language specific subclass. Use it as a template for a new bank or language.
    def __init__(self):
        # First row is the title row of the sheet. It is 9 (Which is 8 when zero based)
        self.firstRow = 8

        # Excel Sheet name
        self.sheetName = "Current Account"

        # Excel column names
        self.dateColumnName = "Date"
        self.creditDebitValueColumnName = "₪ Credit/debit "
        self.debitValueColumnName = None
        self.creditValueColumnName = None
        self.descriptionColumnName = "Description"

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
                            "PURCHASE- .*" + "|" + \
                            "DEPOSIT INTO DEPOSIT ACCOUNT" + "|" + \
                            "TERM PLACEMENT *" + "|" + \
                            "TERM DEPOSIT R PER YOM" + "|" + \
                            "TAX DEDUCTION DUE TO SECURITIES-" +"|" + \
                            "TAX ON PROFIT FROM DEPOSIT" + "|" + \
                            "TAX ON MATURITY OF DEPOSIT" + "|" + \
                            "TAX ON PROFIT FROM RENEWED DEP"

        # Expenses that were returned to me via BIT(like Venmo). We assume that anything coming from BIT is the return of an expense.
        # It could also be other things like the sale of a personal item, however that can also be considered a negative expense.
        self.includeRegex = ".*Transfer From Account 12-799-0095-000000000.*"

        # Everything here is income (Salary etc.)
        self.incomeRegex = "SALARY"
        
        # Anything equal to and above this is an extraordinary expense.
        # We show results that both exclude and include extraordinary expenses.
        self.extraordinaryExpenseFloor = 10000

    def tryToGetDataFromFile(fileName):
        # Try to identify the bank/language according to the name of the file.
        # If not, we could look inside the file.
        if re.search("Current Account.*_....\.xlsx",fileName):
                # Load spreadsheet
            xl = pd.ExcelFile(fileName)

            #print(xl.sheet_names)

            # First row is the title row of the sheet. It is 9 (Which is 8 when zero based)
            firstRow = 8
            # Load a sheet into a DataFrame by name: df1. First row is 9 (Which is 8 when zero based)
            dataframe = xl.parse("Current Account", header=firstRow)
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

analyzer = None
# Select an analyzer

df = TransactionAnalyzer_BankDiscountEnglish.tryToGetDataFromFile(fileName)
if df is not None:
    analyzer = TransactionAnalyzer_BankDiscountEnglish()

# Customize these
# These are expenses that are paid directly out of your salary and do not go through any bank account or credit card.
nonBankMonthlyExpenses = [\
                          ["Company meal card",500],\
                          ["Company car",0],\
                          ["Company medical insurance",0]\
                         ]

# Analyze if we found a suitable analyzer
if analyzer:
    analyzer.analyze(df, nonBankMonthlyExpenses)
else:
    print("The bank could not be identified from the file.")
    
	