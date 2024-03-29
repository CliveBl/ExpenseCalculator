############################################################
# Note: This is work in progress.
############################################################
# Generate a PDF file of your transactions as follows:
# 1. Open the Pepper application on your device.
# 3. Go to your profile using the bottom bar.
# 4. Open "Documents" from the menu.
# 5. Select "Generate new document" from the menu.
# 6. Select "Details of transactions between dates".
# 7. Select a full year.
# 8. Wait for the document to appear in "Documents/My account".
# 9. Send it from the Downloads folder to your computer for processing.
# Run as follows in Windows Terminal:
# (You can run it in Windows cmd, but it does not support languages other than English)
# python pepper.py ".\Monthly account statement-3.pdf"

# You may need to make the following installs
# python.exe -m pip install --upgrade pip
# pip install pandas
# pip install openpyxl
# pip install tabula-py
# Also install Java from https://www.java.com/download/ie_manual.jsp

from transactionAnalyzer import TransactionAnalyzer
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
            # Read the pdf. Generates a list of DataFrames.
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
