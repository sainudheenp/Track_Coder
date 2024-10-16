import openpyxl
import os
import datetime
import pandas as pd



# calulate total minutes from xl sheet sting value
def time_to_mins(time_string):
    hours,mins = map(int, time_string.split(':'))
    return hours * 60 + mins

# printing and total min into hours ,mins
def minutes_time(total_time):
    hours = total_time // 60
    minutes = total_time % 60
    return f"{hours:02}:{minutes:02}"



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

            df =pd.read_excel(os.path.expanduser("~/TrackCoder/trackcoder.xlsx"))
            html_total = df["HTML"].sum()
            css_total = df["CSS"].sum()
            js_total = df["JS"].sum()
            print(html_total , js_total ,css_total)

            total_mins = df["CT"].apply(time_to_mins).sum()
            total_times = minutes_time(total_mins)
            print("CT",total_times)

            total_mins = df["ACT"].apply(time_to_mins).sum()
            total_times = minutes_time(total_mins)
            print("act",total_times)

            total_mins = df["Focus"].apply(time_to_mins).sum()
            total_times = minutes_time(total_mins)
            print("Focus",total_times)




    except Exception as e:
            print("Error",e)

# xl_rw()


