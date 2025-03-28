# Track_Coder Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Modules and Components](#modules-and-components)
6. [Workflow](#workflow)
7. [Troubleshooting](#troubleshooting)

## Project Overview
Track_Coder is a tool designed to automatically track and collect coding metrics to help developers understand their coding habits and productivity. The tool fetches data from various sources including coding activity time and typing speed measurements.

## Installation

### Prerequisites
- Python 3.6+
- Chrome browser (for web scraping)
- Internet connection

### Setup
```bash
# Clone the repository
git clone https://github.com/sainudheenp/Track_Coder.git
cd Track_Coder

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials
```

## Configuration
The application uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

```
# MonkeyType credentials
userEmail_monkey=your_email@example.com
password_monkey=your_password

# Other service credentials (if applicable)
# SERVICE_USERNAME=username
# SERVICE_PASSWORD=password

# Configuration options
# HEADLESS_BROWSER=True
# CHROME_DRIVER_PATH=/path/to/chromedriver
```

## Usage

### Running the Application
```bash
# Run the main application
python main.py

# Get typing speed metrics only
python -c "from utils.typing_wpm import get_wpm; print(get_wpm())"
```

## Modules and Components

### 1. Typing Speed Tracker
This module connects to [MonkeyType](https://monkeytype.com) and retrieves your average typing speed (WPM).

**Key Files:**
- `utils/typing_wpm.py`: Contains functionality to fetch typing speed metrics.
- `utils/get_driver.py`: Browser driver setup and configuration.

### 2. Code Time Tracker
Tracks active coding time from your preferred coding platforms.

**Key Functions:**
- Retrieves daily active code time
- Formats and displays time in hours and minutes
- Stores historical data

## Workflow

1. **Initialization**:
   - The application loads environment variables and configurations.
   - Sets up web drivers for browser automation.

2. **Data Collection**:
   - Connects to MonkeyType to retrieve typing speed data.
   - Retrieves active code time from development platforms.
   - Collects Lines of Code from Local Storage

3. **Data Processing**:
   - Parses raw data into usable metrics.
   - Calculates derived statistics.

4. **Reporting**:
   - Displays metrics in a readable format.
   - Optionally exports data to files or databases.

## Troubleshooting

### Common Issues
1. **Driver Installation Issues**
   - Ensure Chrome is installed on your system.
   - Try manually specifying the Chrome driver path in your .env file.

2. **Authentication Failures**
   - Verify your credentials in the .env file.
   - Check for any account login issues on the respective websites.

3. **Data Not Loading**
   - Check your internet connection.
   - Verify the websites haven't changed their UI structure.

### Support
For issues, please open a ticket in the GitHub repository 

---

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
