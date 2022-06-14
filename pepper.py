############################################################
# Note: This is work in progress.
############################################################
# Generate an Excel file of your transactions as follows:
# 1. Login to Bank in a browser
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
# Also install Java from https://www.java.com/download/ie_manual.jsp

from expenseCalc import TransactionAnalyzer
import sys
import re
import tabula
import pandas as pd

class TransactionAnalyzer_Pepper(TransactionAnalyzer):
    # This a bank/language specific subclass. Use it as a template for a new bank or language.
    def __init__(self):
 
        self.bankName = "Pepper"
        self.currency = "Shekels"

        # Excel column names
        # In Pepper they use some crazy Hebrew encoding. It looks OK in pdf, but when copied this is what we get.
        self.dateColumnName = "ךיראת"
        self.creditDebitValueColumnName = None
        self.creditValueColumnName = "תמאך"
        self.debitValueColumnName = "האוח"
        # There can only be a single description column, so if there are more in the data they must be combined.
        self.descriptionColumnName = "ךיאר"
        # format argument of pandas.to_datetime
        self.dateFormat = "%d.%m.%Y"

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


    # Return a DatFrame or None if the file could not be identified for this class.
    def getDataFrame(fileName):
        # Try to identify the bank/language according to the name of the file.
        # If not, we could look inside the file.
        if re.search("Monthly account statement.*\.pdf",fileName):
            # Read the pdf. Generats a list of DataFrames.
            dataframeList = tabula.read_pdf(fileName, pages='all',encoding="utf-8")
            # Count pages
            pageCount = len(dataframeList)

            df_combined = pd.DataFrame([])
            #tabula.convert_into(fileName, "postbank.csv", output_format="csv", pages='all')
            
            # Combine all pages into one DataFrame
            for page in range(pageCount):
                df_combined = pd.concat([df_combined,dataframeList[page]],ignore_index=True)
               
            # Pepper statements are oldest to newest so we must reverse this as the algorithm expects newest first.
            df_combined = df_combined.sort_index(ascending=False)
            # Now reset the index column.
            df_combined.reset_index(drop=True,inplace=True)
            
            # For debugging
            #print(df_combined)
            return df_combined
        else:
            return None
            
            
# Main
# Check arguments
if len(sys.argv) != 2:
    print("Please specify a pdf file with 12 months of transactions on the command line.")
    exit()

# First argument is the Spreadsheet filename. Ignore the rest.
fileName = sys.argv[1]

# Customize these
# These are expenses that are paid directly out of your salary and do not go through any bank account or credit card.
nonBankMonthlyExpenses = [\
                         ]

df = TransactionAnalyzer_Pepper.getDataFrame(fileName)
if df is not None:
    TransactionAnalyzer_Pepper().analyze(df, nonBankMonthlyExpenses)
else:
    print("The bank could not be identified from the file: ",fileName)
    
