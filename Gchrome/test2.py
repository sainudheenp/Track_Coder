import openpyxl
import os
import datetime

date = datetime.date.today()

# Corrected file extension
Xl_path = os.path.expanduser("~/TrackCoder/trackcoder.xlsx")

if os.path.exists(Xl_path):
    workbook = openpyxl.load_workbook(Xl_path)  # Load existing workbook
    sheet = workbook.active  # Select the active sheet
else:
    workbook = openpyxl.Workbook()  # Create a new workbook
    sheet = workbook.active  # Now the sheet variable will not be None
    sheet.append(["Date", "Focus", "Wpm", "Code Time", "Active Code Time"])  # Append headers

new_data = [
    [date, "1:30", "29", "7:30", "3:30"]
]

for row in new_data:
    sheet.append(row)  # Append new data

workbook.save(Xl_path)  # Save the workbook
print("Data added successfully!")
