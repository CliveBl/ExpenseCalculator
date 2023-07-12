# Generate an Excel file of your transactions as follows:
# 1. Login to Bank in a browser
# 2. Set to English
# 3. Go to your Current Account transactions.
# 4. Select 12 months of transactions using the menu.
# 5. Select Export to Excel using the Export menu.
# 6. Save the file.
# Run as follows in Windows Terminal:
# (You can run it in Windows cmd, but it does not support languages other than English)
# python bankDiscount.py Current Account_29052022_0749.xlsx

from transactionAnalyzer import TransactionAnalyzer
import re
import pandas as pd


class TransactionAnalyzer_BankDiscountEnglish(TransactionAnalyzer):
    # This a bank/language specific subclass. Use it as a template for a new bank or language.
    def __init__(self, creditDebitValueColumnName):

        self.bankName = "Bank Discount"
        self.currency = "Shekels"

        # Excel column names
        self.dateColumnName = "Value date"
        self.creditDebitValueColumnName = creditDebitValueColumnName
        self.debitValueColumnName = None
        self.creditValueColumnName = None
        # There can only be a single description column, so if there are more in the data they must be combined.
        self.descriptionColumnName = "Description"
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
                            "PURCHASE- .*" + "|" + \
                            "DEPOSIT INTO DEPOSIT ACCOUNT" + "|" + \
                            "TERM PLACEMENT *" + "|" + \
                            "TERM DEPOSIT R PER YOM" + "|" + \
                            "TAX DEDUCTION DUE TO SECURITIES-" +"|" + \
                            "TAX ON PROFIT FROM DEPOSIT" + "|" + \
                            "TAX ON MATURITY OF DEPOSIT" + "|" + \
                            "TAX PAID AT SOURCE" + "|" + \
                            "TAX ON PROFIT FROM RENEWED DEP"

        # Expenses that were returned to me via BIT(like Venmo). We assume that anything coming from BIT is the return of an expense.
        # It could also be other things like the sale of a personal item, however that can also be considered a negative expense.
        self.includeRegex = ".*Transfer From Account 12-799-0095-000000000.*"

        # Everything here is income (Salary etc.)
        self.incomeRegex = "SALARY" + "|" +\
                           "CREDIT FROM MASAV"
        
        # Anything equal to and above this is an extraordinary expense.
        # We show results that both exclude and include extraordinary expenses.
        self.extraordinaryExpenseFloor = 26000

    # Return a DatFrame or None if the file could not be identified for this class.
    def getDataFrame(fileName):
        # Try to identify the bank/language according to the name of the file.
        # If not, we could look inside the file.
        if re.search("Current Account.*_....\.xlsx",fileName):
            # Load spreadsheet
            xl = pd.ExcelFile(fileName)

            # print(xl.sheet_names)

            # First row is the title row of the sheet. It is 9 (Which is 8 when zero based)
            firstRow = 8
            # Load a sheet into a DataFrame by name: df1. First row is 9 (Which is 8 when zero based)
            dataframe = xl.parse("Current Account", header=firstRow)
            # Newer sheets titles are at row 8 (Which is 7 when zero based), so we check the first column name.
            if dataframe.columns[0] != "Date":
                firstRow = 7
                # Reload the sheet into a DataFrame by name.
                dataframe = xl.parse("Current Account", header=firstRow)

            return dataframe
        else:
            return None

