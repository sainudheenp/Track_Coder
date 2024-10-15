import json
import os
import base64




# Path to the Base64 encoded JSON file
file_path = os.path.expanduser("~/bin/TrackMe/daily-progress-tracker.json.b64")

def loc():
    try:
        with open(file_path, "r") as enc_json_file:
            # Read the Base64 encoded file content
            encoded_content = enc_json_file.read()

            # Decode the Base64 string
            decoded_content = base64.b64decode(encoded_content).decode('utf-8')

            # Load the decoded content as JSON
            json_data = json.loads(decoded_content)

            # Get the last day entry in the JSON
            last_day = list(json_data.keys())[-1]
            last_lines = json_data[last_day]


        html = last_lines["lines_of_code"]["html"]
        css = last_lines["lines_of_code"]["css"]
        #js = last_lines["lines_of_code"]["js"]
        # total = last_lines["lines_of_code"]["total"]
        total= html + css +js

        return html , css , js , total
    # print(f"HTML    : {html}")
    # print(f"CSS     : {css}")
    # print(f"JS      : {js}")
    # print(f"TOTAL   : {total}")
 except Exception as e:
    print(e)







