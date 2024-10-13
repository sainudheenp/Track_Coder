from utils.typing_wpm import get_wpm
from utils.code_time import get_code_time
from utils.lines_of_code import loc
from utils.xl_rw import xl_rw
from utils.print_values import Print_values

def main():
    try:
        print("Starting....")

        Wpm = get_wpm()
        Focus, ACT, CT = get_code_time()
        html, css, js, total = loc()

        Print_values(Wpm, Focus, ACT, CT, html, css, js, total)
        xl_rw(Focus,Wpm, ACT, CT, html, css, js, total)

    except Exception as e:
        print("Error:", e)

main()

