import os

# Configuration for file paths
BASE_DIR = os.getenv('TRACK_CODER_BASE_DIR', os.path.expanduser("~/TrackCoder"))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Ensure directories exist
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Interactive mode (set to False for Docker)
INTERACTIVE_MODE = os.getenv('TRACK_CODER_INTERACTIVE', 'True').lower() == 'true'