import json
import os
import datetime

file_path = os.path.expanduser("~/TrackMe/daily-progress-tracker.json")

html = 0
css = 0
js =0

with open(file_path) as json_file:
    json_data = json.load(json_file)

    last_day = list(json_data.keys())[-1]
    last_lines = json_data[last_day]


    html = last_lines["lines_of_code"]["html"]
    css = last_lines["lines_of_code"]["css"]
    # js = last_lines["lines_of_code"]["js"]
    total = last_lines["lines_of_code"]["total"]
   
    print(f"HTML    : {html}")
    print(f"CSS     : {css}")
    print(f"JS      : {js}")
    print(f"TOTAL   : {total}")

