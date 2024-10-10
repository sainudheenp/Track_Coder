import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("userEmail_monkey"))
print(os.getenv("password_monkey"))
