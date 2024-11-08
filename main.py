from utils.typing_wpm import get_wpm
from utils.code_time import get_code_time
from utils.lines_of_code import loc
from utils.xl_rw import xl_rw
from utils.print_values import Print_values
from utils.get_driver import get_driver
from utils.total_calc import total_calc
from utils.cfile import copy_past

def main():
    try:
        print("Starting....")

        Wpm = get_wpm()
        Focus , ACT, CT = get_code_time()

        html, css, js, total = loc()

        Days = xl_rw(Focus,Wpm,CT, ACT,  html, css, js, total)

        html_total ,css_total, js_total, CT_TOTAL, ACT_TOTAL,Focus_TOTA ,T_Total  = total_calc()

        Print_values(Wpm, Focus, ACT, CT, html, css, js, total, html_total ,css_total, js_total, CT_TOTAL, ACT_TOTAL,Focus_TOTA ,T_Total , Days)

        copy_past()

    except Exception as e:
        print("Error main:", e)

main()

