import openpyxl
import os
import datetime






def xl_rw(Focus , Wpm ,CT ,ACT,HTML , CSS ,JS,TOTAL ):
    try:
            date = datetime.date.today().strftime("%Y-%m-%d")
            # Days = int(df.iloc[-1]["Days"])  + 1 

            Xl_path = os.path.expanduser("~/TrackCoder/trackcoder.xlsx")

            os.makedirs(os.path.dirname(Xl_path), exist_ok=True)

            if os.path.exists(Xl_path):
             workbook = openpyxl.load_workbook(Xl_path)
             sheet = workbook.active
            else:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.append(["Date", "Focus", "Wpm", "CT", "ACT" ,"HTML" , "CSS","JS","Total","Days"])
            
            days_column = [cell.value for cell in sheet['J'] if cell.value is not None and isinstance(cell.value, int)]
            Days = days_column[-1] + 1 


            print("ct",CT)
            print("act",ACT)

            new_data = [
            [date, Focus, Wpm, CT, ACT, HTML , CSS , JS , TOTAL , Days]
            ]


            date_column = sheet['A']
            dates = [cell.value for cell in date_column if cell.value is not None]
            if date in dates :
                print(f" \n Data for {date} already exists in the Excel sheet. No new entry added.")
            else :
                for row in new_data:
                    sheet.append(row)
                    workbook.save(Xl_path)

                print(" \n Data added to XL-Sheets successfully")
            
            
     



#calculating sum








    except Exception as e:
            print("Error",e)

    finally :
        return Days

# xl_rw()


