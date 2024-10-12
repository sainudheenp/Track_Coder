import openpyxl
import os
import datetime

date = datetime.date.today()

# Corrected file extension
Xl_path = os.path.expanduser("~/TrackCoder/trackcoder.xlsx")

if os.path.exists(Xl_path):
    workbook = openpyxl.load_workbook(Xl_path)
    sheet = workbook.active
else:
    open(Xl_path, 'a').close()
    workbook = openpyxl.Workbook(Xl_path)
    sheet = workbook.active
    sheet.append(["Date", "Focus", "Wpm", "Code Time", "Active Code Time"])

new_data = [
    [date, "1:30", "29", "7:30", "3:30"]
]

for row in new_data:
    sheet.append(row)  # Append new data

workbook.save(Xl_path)
print("Data added successfully!")
