from utils.code_time import get_lines_of_code
from utils.typing_data import get_typing_data


def main():
    try:
        get_typing_data()
        get_lines_of_code()

    except Exception as e :
        print("error" , e)

        
