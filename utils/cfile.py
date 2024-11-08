import shutil
import os
def copy_past() :
    try :
        shutil.copy(os.path.expanduser("~/TrackCoder/trackcoder.xlsx"),os.getcwd())
    except Exception as e:
        print("C_File Error")
