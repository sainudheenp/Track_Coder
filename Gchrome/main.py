from utils.code_time import get_code_time
from utils.typing_wpm import get_typing_data
from utils.lines_of_code import *


def main():
    try:
        get_typing_data()
        get_code_time()

    except Exception as e :
        print("error" , e)


