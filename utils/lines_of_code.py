import json
import os
import base64
from datetime import datetime, timedelta





file_path = os.path.expanduser("~/bin/TrackMe/daily-progress-tracker.json.b64")


def loc():
        try:
            html = 00
            css = 00
            js = 00

            with open(file_path, "r") as enc_json_file:
             encoded_content = enc_json_file.read()

            decoded_content = base64.b64decode(encoded_content).decode('utf-8')
            json_data = json.loads(decoded_content)


            today = datetime.now()
            yesterday = today - timedelta(days=1)
            loc_date = yesterday.strftime("%m/%d/%Y")
            # print(loc_date)


            if loc_date in json_data:
                    lines_of_code = json_data[loc_date]["lines_of_code"]
                    html = lines_of_code.get("html",00)
                    css = lines_of_code.get("css",00)
                    js = lines_of_code.get("javascript",00)
            # except Exception as e :
            #     total= html + css + js
            #     return html , css , js , total


            total= html + css + js

            return html , css , js , total

        except Exception as e:
                     print("LOC Error :  ",e)



