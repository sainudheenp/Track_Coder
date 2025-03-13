from utils.typing_wpm import get_wpm
from utils.code_time import get_code_time
from utils.lines_of_code import loc
from utils.xl_rw import xl_rw
from utils.print_values import Print_values
from utils.get_driver import get_driver
from utils.total_calc import total_calc
from utils.cfile import copy_past
import argparse
from datetime import datetime, timedelta


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-date", default=(datetime.today()- timedelta(days=1)).strftime("%Y-%m-%d"), help="Specify a date (YYYY-MM-DD)")
    args = parser.parse_args()
    yesterday = args.date



    try:
        # print(f"Starting....{args.date}")
        print("\n" + "=" * 50)
        print(f"🚀 **Track Coder Automation Started** 📊")
        print(f"📅 Date: **{yesterday}**")
        print("=" * 50 + "\n")

#date arg


        Wpm = get_wpm()

        Focus , ACT, CT = get_code_time(yesterday)

        html, css, js, total = loc(yesterday)

        Days = xl_rw(Focus,Wpm,CT, ACT,  html, css, js, total,yesterday=yesterday)

        html_total ,css_total, js_total, CT_TOTAL, ACT_TOTAL,Focus_TOTA ,T_Total  = total_calc()

        Print_values(Wpm, Focus, ACT, CT, html, css, js, total, html_total ,css_total, js_total, CT_TOTAL, ACT_TOTAL,Focus_TOTA ,T_Total , Days)

        copy_past()

    except Exception as e:
        print("Error main:", e)

main()

