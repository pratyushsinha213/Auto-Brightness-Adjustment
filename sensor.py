import urllib.request
import time
import webbrowser
import threading
import os
from datetime import datetime
from PIL import Image, ImageEnhance
import pandas as pd
import matplotlib.pyplot as plt

# PhyPhox server configuration
IPAddress = '192.168.1.6:8080'  # Replace with your PhyPhox IP
num_data = 5  # Number of data pulls in each session
pause_tm = 2  # Time interval between data collections in seconds

# URLs for data management
save_dat = f'http://{IPAddress}/export?format=0'
clear_dat = f'http://{IPAddress}/control?cmd=clear'
start_dat = f'http://{IPAddress}/control?cmd=start'

# Load the image for brightness adjustment
image_path = "image.png"
image = Image.open(image_path)

def lux_to_brightness(lux):
    """Convert Lux value to a brightness factor."""
    if lux < 100:
        return 0.5
    elif lux < 1000:
        return 1.0
    elif lux < 5000:
        return 1.5
    else:
        return 2.0

def collect_data():
    """Collect data and save using Chrome, with timestamped file names."""
    for _ in range(num_data):
        timestamp = datetime.now().strftime("Light %Y-%m-%d_%H-%M-%S")
        webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open(save_dat)
        print(f"Data collected: {timestamp}")
        time.sleep(pause_tm)

def clear_and_restart_collection():
    """Clear and restart data collection."""
    urllib.request.urlopen(clear_dat)
    print("Data cleared.")
    urllib.request.urlopen(start_dat)
    print("Data collection restarted.")

def continuous_data_collection():
    """Thread function for continuous data collection."""
    while True:
        collect_data()
        clear_and_restart_collection()

def get_lux_values_from_excel(file_path):
    """Read Lux values from the Excel file."""
    try:
        df = pd.read_excel(file_path)
        lux_values = df['Illuminance (lx)'].tolist()
        return lux_values
    except Exception as e:
        print("Error reading Excel file:", e)
        return []

def adjust_image_brightness(file_path):
    """Adjust image brightness based on Lux data and display the image."""
    lux_values = get_lux_values_from_excel(file_path)
    for lux in lux_values:
        brightness_factor = lux_to_brightness(lux)
        enhancer = ImageEnhance.Brightness(image)
        brightened_image = enhancer.enhance(brightness_factor)

        # Display the adjusted image using matplotlib
        plt.imshow(brightened_image)
        plt.title(f"Brightness Adjusted by Lux: {lux} lx")
        plt.axis('off')
        plt.pause(2)  # Pause to allow for viewing the adjusted image
    
    plt.show()  # Keep the final image displayed

def main_data_logging():
    """Main function to start data logging and brightness adjustment in threads."""
    urllib.request.urlopen(start_dat)  # Start initial data collection
    data_thread = threading.Thread(target=continuous_data_collection)
    data_thread.daemon = True  # Stops when the main program exits
    data_thread.start()

    # Adjust brightness periodically based on the most recent Excel file generated
    plt.ion()  # Enable interactive mode for real-time updates
    while True:
        latest_file = max(
            (f for f in os.listdir() if f.startswith("Light") and f.endswith(".xlsx")),
            key=os.path.getctime,
            default=None
        )
        if latest_file:
            adjust_image_brightness(latest_file)
        time.sleep(10)  # Frequency of checking for new files and adjusting brightness

# Start the main logging and brightness adjustment processes
if __name__ == "__main__":
    main_data_logging()
