############################################################
# Note: This is work in progress.
############################################################
# Generate an Excel file of your transactions as follows:
# 1. Login to Bank in a browser
# 2. Set to English (Hebrew can be supported by adjusted the script)
# 3. Go to your Current Account transactions.
# 4. Select 12 months of transactions using the menu.
# 5. Select Export to Excel using the Export menu.
# 6. Save the file.
# Run as follows in Windows Terminal:
# (You can run it in Windows cmd, but it does not support languages other than English)
# python pepper.py ".\Monthly account statement-3.pdf"

# You may need to make the following installs
# python.exe -m pip install --upgrade pip
# pip install pandas
# pip install openpyxl
# pip install tabula-py

from expenseCalc import TransactionAnalyzer
import sys
import re
import tabula

class TransactionAnalyzer_Pepper(TransactionAnalyzer):
    # This a bank/language specific subclass. Use it as a template for a new bank or language.
    def __init__(self):
        # First row is the title row of the sheet. It is 9 (Which is 8 when zero based)
        self.firstRow = 8

        # Excel Sheet name
        self.sheetName = "Current Account"

        # Excel column names
        self.dateColumnName = "Date"
        self.creditDebitValueColumnName = None
        self.creditValueColumnName = "זכות"
        self.debitValueColumnName = "חובה"
        self.descriptionColumnName = "תאור פעולה"

        # Transfers to my accounts and investment costs:
        # Purchase of shares
        # Savings account
        # Savings account
        # Savings account
        # Tax on savings
        # Tax on savings
        # Tax on savings
        # Tax on savings
        self.excludeRegex = "DummyRegex"

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
        if re.search("Monthly account statement.*\.pdf",fileName):
            dataframe = tabula.read_pdf(fileName, pages='all')[0]
            # convert PDF into CSV
            #tabula.convert_into(fileName, "postbank.csv", output_format="csv", pages='all')
            if dataframe is not None:
                print(dataframe)
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

df = TransactionAnalyzer_Pepper.tryToGetDataFromFile(fileName)
if df is not None:
    analyzer = TransactionAnalyzer_Pepper()

# Customize these
# These are expenses that are paid directly out of your salary and do not go through any bank account or credit card.
nonBankMonthlyExpenses = [\
                          ]

# Analyze if we found a suitable analyzer
if analyzer:
    analyzer.analyze(df, nonBankMonthlyExpenses)
else:
    print("The bank could not be identified from the file.")