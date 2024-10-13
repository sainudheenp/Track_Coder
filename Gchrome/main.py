from utils.code_time import get_code_time
from utils.typing_wpm import get_typing_data
from utils.lines_of_code import loc
from utils.xl_rw import xl_rw

def main():
    try:
        print("Starting....")

        Wpm = get_typing_data()

        Focus, ACT, CT = get_code_time()

        html , css , js, total = loc()


        Print_values( Wpm, Focus, ACT,CT, html, css, js, total)

        xl_rw(Wpm, Focus, ACT,CT, html, css, js, total)



    except Exception as e:
        print("Error:", e)

# if __name__ == "__main__":

def Print_values (Wpm , Focus, ACT ,CT , html,css,js,total):
        print(f"Typing  : {Wpm}")
        print(f"Focus   : {Focus}")
        print(f"ACT     : {ACT}")
        print(f"CT      : {CT}")
        print(f"HTML    : {html}")
        print(f"CSS     : {css}")
        print(f"JS      : {js}")
        print(f"TOTAL   : {total}")








main()
