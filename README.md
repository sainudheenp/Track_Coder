<h1>Track Coder - Automation Project</h1>


This project automates the process of gathering coding-related statistics such as typing speed (WPM), focus time, active code time, and lines of code written in HTML, CSS, and JavaScript. The data is scraped from various sources such as Software.com (for code time) and MonkeyType (for typing data) using Selenium and Python  to . Additionally, this project features the ability to log the data into an Excel sheet for reporting.
Features

    Typing Speed: Automatically retrieves typing speed (WPM)  from MonkeyType.
    Code Time: Scrapes active code time and focus time from Software.com dashboard using Selenium automation.
    Lines of Code: Collects the number of lines written in HTML, CSS, and JavaScript.
    Excel Export: Logs all gathered statistics into an Excel file.

Prerequisites
For Local Setup:

    Python 
    Selenium
    Pandas
    OpenPyXL
    Dotenv
    Google Chrome
    VSCode Extensions:
                TrackMe  - v3.1.0
                Codetime - v2.8.1



For Docker Setup:

    Docker (installed and running on the system)

Installation

   Clone the repository:

     git clone https://github.com/sainudheenp/track_coder.git
     cd track_coder

Set up the environment: Create a virtual environment and install dependencies:


    python -m venv myenv
    source myenv/bin/activate
    pip install -r requirements.txt


Configure Environment Variables: Create a .env file in the root directory with the following variables:

    # monkeytype.com
    userEmail_monkey=@gmail.com
    password_monkey=Password


    # app.software.com
    userEmail_code_time=@gmail.com
    password_code_time=password






Running the Project Locally

To run the project locally, execute the following:

     python main.py

     


Excel Output Path

The collected data will be saved in an Excel file located at:


    /username/trackcoder/output.xlsx

Screenshot Output Path:

    /username/trackcoder/screenshots





