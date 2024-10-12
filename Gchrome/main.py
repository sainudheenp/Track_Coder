# from utils.code_time import get_code_time
# from utils.typing_wpm import get_typing_data
# from utils.lines_of_code import *
# from utils.xl_rw import xl_rw


# List of utils files
util_files = [
    "utils.typing_wpm",
    "utils.code_time",
    "utils.lines_of_code",
    "utils.xl_rw"
]

for util_file in util_files:
    try:
        module = __import__(util_file, fromlist=['*'])
    except Exception as e:
        print("Something Went Wrong!" ,e)




# def main():
#     try:
#         get_typing_data()
#         get_code_time()
#         xl_rw()

#     except Exception as e :
#         print("error" , e)


