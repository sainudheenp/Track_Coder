import openpyxl
import os
import datetime






def xl_rw(Focus , Wpm ,CT ,ACT,HTML , CSS ,JS,TOTAL):
    try:
            date = datetime.date.today().strftime("%Y-%m-%d")

            Xl_path = os.path.expanduser("~/TrackCoder/trackcoder.xlsx")

            os.makedirs(os.path.dirname(Xl_path), exist_ok=True)

            if os.path.exists(Xl_path):
             workbook = openpyxl.load_workbook(Xl_path)
             sheet = workbook.active
            else:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.append(["Date", "Focus", "Wpm", "CT", "ACT" ,"HTML" , "CSS","JS","Total"])

            new_data = [
            [date, Focus, Wpm, CT, ACT, HTML , CSS , JS , TOTAL]
            ]


            date_column = sheet['A']
            dates = [cell.value for cell in date_column if cell.value is not None]
            if date in dates :
                print(f"Data for {date} already exists in the Excel sheet. No new entry added.")
            else :
                for row in new_data:
                    sheet.append(row)
                    workbook.save(Xl_path)
                print("Data added successfully!")



#calculating sum








    except Exception as e:
            print("Error",e)

# xl_rw()


