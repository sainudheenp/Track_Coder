import openpyxl
import os
from datetime import datetime, timedelta
from config_paths import OUTPUT_DIR







def xl_rw(Focus , Wpm ,CT ,ACT,HTML , CSS ,JS,TOTAL ,yesterday):
    try:
            # date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

            yesterday = datetime.strptime(yesterday,"%Y-%m-%d")
            date = yesterday.strftime("%Y-%m-%d")


            Xl_path = os.path.join(OUTPUT_DIR, "trackcoder.xlsx")

            os.makedirs(OUTPUT_DIR, exist_ok=True)

            if os.path.exists(Xl_path):
             workbook = openpyxl.load_workbook(Xl_path)
             sheet = workbook.active
            else:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.append(["Date", "Focus", "Wpm", "CT", "ACT" ,"HTML" , "CSS","JS","Total","Days"])


            date_column = sheet['A']
            dates = [cell.value for cell in date_column if cell.value is not None]


            try :
                days_column = [cell.value for cell in sheet['J'] if cell.value is not None and isinstance(cell.value, int)]
                if date in dates :
                    Days = int(days_column[-1])
                else :
                    Days =  int(days_column[-1]) + 1
            except Exception as e :
                Days = 1




            new_data = [
            [date, Focus, Wpm, CT, ACT, HTML , CSS , JS , TOTAL , Days]
            ]


            if date in dates :
                print(f"\n❗ \033[1mData for {date} already exists in the Excel sheet.\033[0m")
            else :
                for row in new_data:
                    sheet.append(row)
                    workbook.save(Xl_path)
                print("\n\n\u2705\033[1m Data added to XL-Sheets successfully\033[0m")






#calculating sum








    except Exception as e:
            print("Error xl",e)

    finally :
        return Days

# xl_rw()


