# The Effortless Monthly Expense Calculator
#
# By Clive Bluston
# 12th July 2023
#
#  Up until now all tools that help you calculate your monthly expenses require you to collect
# and enter them into some sort of expense calculator. This requires a lot of effort and is
# error-prone.
# This script extracts the information directly from your bank account transactions.
# It will work well even if you have multiple back accounts, investments and credit cards.
# The only condition is that all your expenses eventually land in your current account. This is
# the case for most people.
#
# The script calls the bank specific subclasses, one by one, until one that understands the
# transaction file that is supplied as an argument is found.
# Banks and languages can be added just by creating a new subclass of TransactionAnalyzer
# Use TransactionAnalyzer_BankDiscountEnglish as a template.
#
# Run as follows in Windows Terminal:
# (You can run it in Windows cmd, but it does not support file name languages other than English)
# python expenseCalculator.py Current Account_29052022_0749.xlsx

# You may need to make the following installs:
# python.exe -m pip install --upgrade pip
# python.exe -m pip install -r requirements.txt
# pip install pandas
# pip install openpyxl
# pip install matplotlib
# pip install parse

# For pdf statements only:
# pip install tabula-py

# Also install Java from
# Windows: https://www.java.com/download/ie_manual.jsp
# Linux: sudo apt install default-jre
#

import sys
import os
import webbrowser

###################################################################
# One import per bank.
import bankDiscountHebrew
import bankDiscount
import pepper
import bankHapoalim
import bankYahav
import postalBank
####################################################################

# Main

# Check Python version.
if not sys.version_info >= (3, 8):
    print("Minimum Python version required is 3.8. You are running:")
    print(sys.version_info)
    exit()

# Check arguments. The only valid case is a single argument.
if len(sys.argv) != 2:
    print("Please specify an xlsx/pdf file with 12 months of transactions on the command line.")
    exit()

# First argument is the Spreadsheet filename. Ignore the rest.
fileName = sys.argv[1]

# Check that the file exists.
if os.path.isfile(fileName):
    print("Using file: ", os.path.abspath(fileName))
else:
    print("File does not exist: ",os.path.abspath(fileName))
    exit()

# Try each bank.
# Add a condition for each additional bank here.
if (df := bankDiscountHebrew.TransactionAnalyzer_BankDiscountHebrew.getDataFrame(fileName)) is not None:
    t = bankDiscountHebrew.TransactionAnalyzer_BankDiscountHebrew()
elif (df := bankDiscount.TransactionAnalyzer_BankDiscountEnglish.getDataFrame(fileName)) is not None:
    # Pass the creditDebitValueColumnName (fourth column), because it changes from time to time.
    t = bankDiscount.TransactionAnalyzer_BankDiscountEnglish(df.columns[3])
elif (df := postalBank.TransactionAnalyzer_PostalBankHebrew.getDataFrame(fileName)) is not None :
    t = postalBank.TransactionAnalyzer_PostalBankHebrew()
elif (df := bankYahav.TransactionAnalyzer_BankYahav.getDataFrame(fileName)) is not None:
    t = bankYahav.TransactionAnalyzer_BankYahav()
elif (df := bankHapoalim.TransactionAnalyzer_BankHapoalim.getDataFrame(fileName)) is not None:
    t = bankHapoalim.TransactionAnalyzer_BankHapoalim()
elif (df := pepper.TransactionAnalyzer_Pepper.getDataFrame(fileName)) is not None:
    t = pepper.TransactionAnalyzer_Pepper()
else:
    print("The bank could not be identified from the file: ", fileName)
    print("You may need to add support for the bank.")
    exit()


# Customize these.
# These are expenses that are paid directly out of your salary and do not go through any bank account or credit card.
nonBankMonthlyExpenses = [\
                          ["Company meal card",250],\
                          ["Company car",0],\
                          ["Company medical insurance",80]\
                         ]

# Analyze
t.analyze(df, nonBankMonthlyExpenses)

# Render to console.
# t.renderConsole()

# Render to HTML
htmlFileName = os.path.splitext(fileName)[0] + ".html"
t.renderHTML(htmlFileName)

# Open results in default browser. We need to use the full path otherwise it will be opened with MS IE.
webbrowser.open(os.path.join('file://', os.path.realpath(htmlFileName)))
