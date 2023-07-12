# Test ExpenseCalculator Windows Powershell script
#
# Note that in order to handle UTF-8 file names correctly this file must have UTF-8 BOM at its beginning (EF BB EF).
#
#
#
echo "XXX" > testmode.tmp
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass -Force
rm *_config.json
python repo\ExpenseCalculator\expenseCalculator.py xxxxx

python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\עובר ושב_12062022_1710.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\עובר ושב_04072023_1640.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\Current Account_12062022_1609.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\Current Account_06072023_1917.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\Movement.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\Monthly account statement-3.pdf"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\excelNewTransactions.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\תנועות בחשבון עו״ש (1).xlsx"
# Run again with config files
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\עובר ושב_12062022_1710.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\עובר ושב_04072023_1640.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\Current Account_12062022_1609.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\Current Account_06072023_1917.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\Movement.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\Monthly account statement-3.pdf"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\excelNewTransactions.xlsx"
python repo\ExpenseCalculator\expenseCalculator.py "C:\Users\clive\expenseCalc\תנועות בחשבון עו״ש (1).xlsx"
rm testmode.tmp
