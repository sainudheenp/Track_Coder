import os
import pandas as pd

def times_to_min(time_str) :
    hours,mins = map(int, time_str.split(":"))
    return hours * 60 +  mins

def minutes_to_time(total_mins) :
    hours = total_mins // 60
    mins = total_mins % 60
    return f"{hours:02}:{mins:02}"




df = pd.read_excel(os.path.expanduser("~/TrackCoder/trackcoder.xlsx"))

total__mins = df["CT"].apply(times_to_min).sum()

print(total__mins)

total_ct = minutes_to_time(total__mins)
print(total_ct)