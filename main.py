from utils.typing_wpm import get_wpm
from utils.code_time import get_code_time
from utils.lines_of_code import loc
from utils.xl_rw import xl_rw
from utils.print_values import Print_values
from utils.get_driver import get_driver
from utils.total_calc import total_calc
from utils.cfile import copy_past
# let's assume your screenshot function is called `screenshot_xl`
from utils.screenshot_xl import screenshot_xl  # <-- your function here

import argparse
from datetime import datetime, timedelta


def main():
    parser = argparse.ArgumentParser(description="Track coder automation tool")

    # Regular date argument (for normal daily run)
    parser.add_argument(
        "-date",
        default=(datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
        help="Specify a date (YYYY-MM-DD). Default: yesterday"
    )

    # scrxl argument (two date range for screenshot/Excel mode)
    parser.add_argument(
        "-scrxl",
        nargs=2,
        metavar=("START_DATE", "END_DATE"),
        default=None,
        help="Run screenshot/Excel generation for a date range: START_DATE END_DATE"
    )

    args = parser.parse_args()

    # If user provides -scrxl, run screenshot mode only
    if args.scrxl:
        scrxl_start, scrxl_end = args.scrxl
        print("\n" + "=" * 50)
        print("📸 Running Screenshot & Excel Mode")
        print(f"Start date: {scrxl_start}")
        print(f"End date:   {scrxl_end}")
        print("=" * 50 + "\n")

        try:
            # Call your screenshot function (replace with your actual name)
            screenshot_xl(scrxl_start, scrxl_end)
            print("✅ Screenshot & Excel generation completed.")
        except Exception as e:
            print("❌ Error in Screenshot mode:", e)
        return  # Exit early — don't run the normal logic

    # Normal daily automation mode
    yesterday = args.date

    try:
        print("\n" + "=" * 50)
        print("🚀 Track Coder Automation Started")
        print(f"📅 Date: {yesterday}")
        print("=" * 50 + "\n")

        Wpm = get_wpm()
        Focus, ACT, CT = get_code_time(yesterday)
        html, css, js, total = loc(yesterday)
        Days = xl_rw(Focus, Wpm, CT, ACT, html, css, js, total, yesterday=yesterday)
        html_total, css_total, js_total, CT_TOTAL, ACT_TOTAL, Focus_TOTAL, T_Total = total_calc()
        Print_values(Wpm, Focus, ACT, CT, html, css, js, total,
                     html_total, css_total, js_total, CT_TOTAL,
                     ACT_TOTAL, Focus_TOTAL, T_Total, Days)
        copy_past()

    except Exception as e:
        print("❌ Error in main mode:", e)


if __name__ == "__main__":
    main()
