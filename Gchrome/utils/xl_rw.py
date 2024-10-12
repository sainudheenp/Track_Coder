import openpyxl
import os
import datetime

date = datetime.date.today()

Xl_path = os.path.expanduser("~/TrackCoder/trackcoder.xlsx")

os.makedirs(os.path.dirname(Xl_path), exist_ok=True)

if os.path.exists(Xl_path):
    workbook = openpyxl.load_workbook(Xl_path)
    sheet = workbook.active
else:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Date", "Focus", "Wpm", "CT", "ACT"])
new_data = [
    [date, "1:30", "29", "7:30", "3:30"]
]
# sheet.column_dimensions['A'].width = 15

for row in new_data:
    sheet.append(row)
workbook.save(Xl_path)
print("Data added successfully!")
