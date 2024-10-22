import pandas as pd
import os


# calulate total minutes from xl sheet sting value
def time_to_mins(time_string):
    hours,mins = map(int , time_string.split(':'))
    print("tm",hours * 60 + mins)
    return hours * 60 + mins

# printing and total min into hours ,mins
def minutes_time(total_time):
    hours = total_time // 60
    minutes = total_time % 60
    print("mt",hours , minutes)
    return f"{hours:02}:{minutes:02}"




def total_calc():
    try:
            df =pd.read_excel(os.path.expanduser("~/TrackCoder/trackcoder.xlsx"))
            # df =pd.read_excel(os.path.expanduser("~/TrackCoder/trackcodersafever.xlsx"))

            html_total = df["HTML"].sum()
            css_total = df["CSS"].sum()
            js_total = df["JS"].sum()
            T_Total  = html_total + css_total + js_total


            # print(html_total , js_total ,css_total)
            total_mins = df["CT"].apply(time_to_mins).sum()
            print("total mins ct",total_mins)
            CT_TOTAL = minutes_time(total_mins)
            # print("CT_TOTAL",CT_TOTAL)

            total_mins = df["ACT"].apply(time_to_mins).sum()
            ACT_TOTAL = minutes_time(total_mins)
            # print("ACT_TOTAL",ACT_TOTAL)

            total_mins = df["Focus"].apply(time_to_mins).sum()
            Focus_TOTAL = minutes_time(total_mins)



            return html_total ,css_total, js_total, CT_TOTAL, ACT_TOTAL,Focus_TOTAL , T_Total
    except Exception as e :
        print(" calc err", e)


# total_calc()