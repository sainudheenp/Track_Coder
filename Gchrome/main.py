from utils.code_time import get_code_time
from utils.typing_wpm import get_typing_data
from utils.lines_of_code import loc

def main():
    try:
        print("Starting....")

        Wpm = get_typing_data()

        Focus, ACT, CT = get_code_time()

        html , css , js, total = loc()






        print(f"Typing  : {Wpm}")
        print(f"Focus   : {Focus}")
        print(f"ACT     : {ACT}")
        print(f"CT      : {CT}")
        print(f"HTML    : {html}")
        print(f"CSS     : {css}")
        print(f"JS      : {js}")
        print(f"TOTAL   : {total}")
    except Exception as e:
        print("Error:", e)

# if __name__ == "__main__":
main()
