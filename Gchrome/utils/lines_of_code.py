import json
import os
import datetime

file_path = os.path.expanduser("~/TrackMe/daily-progress-tracker.json")


with open(file_path) as json_file:
    json_data = json.load(json_file)

    last_day = list(json_data.keys())[-1]
    last_lines = json_data[last_day]



    print(last_lines)