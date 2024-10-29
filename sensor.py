# import requests
# import urllib.request
# import time
# import webbrowser
# from PIL import Image, ImageEnhance
# import threading

# # PhyPhox server details
# phyphox_ip = "http://192.168.1.6:8080"
# lux_endpoint = f"{phyphox_ip}/get?"
# IPAddress = '192.168.1.6:8080'  # IP address and port specified by the phyphox app
# num_data = 5  # Number of data chunks to collect
# pause_tm = 2  # Time to wait in between data collections

# # URLs for data management
# save_dat = f'http://{IPAddress}/export?format=0'
# clear_dat = f'http://{IPAddress}/control?cmd=clear'
# start_dat = f'http://{IPAddress}/control?cmd=start'

# # Load the image
# image = Image.open("image.png")

# def get_lux_value():
#     """Retrieve Lux value from the PhyPhox server."""
#     try:
#         response = requests.get(lux_endpoint)
#         data = response.json()
#         lux_value = data.get('lx')  # Change this to the correct key for Lux value
#         return lux_value
#     except Exception as e:
#         print("Error retrieving Lux data:", e)
#         return None

# def lux_to_brightness(lux):
#     """Convert Lux value to a brightness factor."""
#     if lux is None:
#         return 1.0  # Default brightness if data is unavailable
#     if lux < 100:
#         return 0.5
#     elif lux < 1000:
#         return 1.0
#     elif lux < 5000:
#         return 1.5
#     else:
#         return 2.0

# def continuous_data_collection():
#     """Thread function to continuously download data."""
#     while True:
#         webbrowser.get("C:\Program Files\Google\Chrome\Application\chrome.exe %s").open(save_dat)
#         time.sleep(pause_tm)

# def main_data_logging():
#     """Main function to control data collection and clearing."""
#     urllib.request.urlopen(start_dat)  # Start collecting data

#     # Start a thread for continuous data collection
#     collector_thread = threading.Thread(target=continuous_data_collection)
#     collector_thread.daemon = True
#     collector_thread.start()

#     # Collect and clear data twice
#     for _ in range(2):
#         time.sleep(pause_tm * num_data)  # Wait before the next data request
#         urllib.request.urlopen(clear_dat)  # Clear the data collection
#         urllib.request.urlopen(start_dat)  # Restart data collection

# def adjust_image_brightness():
#     """Continuously adjust image brightness based on real-time Lux data."""
#     while True:
#         lux_value = get_lux_value()
#         brightness_factor = lux_to_brightness(lux_value)
#         enhancer = ImageEnhance.Brightness(image)
#         brightened_image = enhancer.enhance(brightness_factor)

#         # Display and save the adjusted image
#         brightened_image.show()
#         brightened_image.save("adjusted_image.png")

#         time.sleep(2)  # Avoid overwhelming the server

# # Start the main logging function and brightness adjustment in separate threads
# if __name__ == "__main__":
#     main_data_logging()
#     adjust_image_brightness()


import requests
import urllib.request
import time
import webbrowser
from PIL import Image, ImageEnhance
import threading
import pandas as pd

# PhyPhox server details
phyphox_ip = "http://192.168.1.6:8080"  # Replace with your PhyPhox IP
lux_endpoint = f"{phyphox_ip}/get?"
num_data = 5  # Number of data chunks to collect at once
pause_time = 10  # Time to wait in seconds between data pulls

# URLs for data management
save_dat = f'{phyphox_ip}/export?format=0'
clear_dat = f'{phyphox_ip}/control?cmd=clear'
start_dat = f'{phyphox_ip}/control?cmd=start'

# Load the image
image = Image.open("image.png")

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

def url_open_with_retry(url, retries=3, delay=2):
    """Attempt to open a URL with retries."""
    for attempt in range(retries):
        try:
            return urllib.request.urlopen(url)
        except urllib.error.URLError as e:
            print(f"Attempt {attempt + 1}: Failed to connect to {url}. Error: {e}")
            time.sleep(delay)
    print(f"All attempts to connect to {url} failed.")
    return None

def continuous_data_collection():
    """Thread function to continuously download data."""
    while True:
        for _ in range(num_data):
            url_open_with_retry(save_dat)  # Save data
            time.sleep(pause_time)  # Wait before the next data request
        
        # Clear data collection after specified pulls
        url_open_with_retry(clear_dat)  # Clear the data
        url_open_with_retry(start_dat)  # Start new data collection
        time.sleep(pause_time)  # Wait before collecting data again

def adjust_image_brightness(file_path):
    """Continuously adjust image brightness based on Lux data."""
    lux_values = get_lux_values_from_excel(file_path)
    for lux in lux_values:
        brightness_factor = lux_to_brightness(lux)
        enhancer = ImageEnhance.Brightness(image)
        brightened_image = enhancer.enhance(brightness_factor)

        # Display and save the adjusted image
        brightened_image.show()
        brightened_image.save("adjusted_image.png")

        time.sleep(2)  # Avoid overwhelming the server

def get_lux_values_from_excel(file_path):
    """Read Lux values from the Excel file."""
    try:
        df = pd.read_excel(file_path)
        lux_values = df['Illuminance (lx)'].tolist()  # Extract Lux values from the column
        return lux_values
    except Exception as e:
        print("Error reading Excel file:", e)
        return []

def main_data_logging():
    """Main function to start the data logging process."""
    url_open_with_retry(start_dat)  # Start data collection
    # Start the thread for continuous data collection
    collector_thread = threading.Thread(target=continuous_data_collection)
    collector_thread.daemon = True  # Daemonize thread to exit when the main program exits
    collector_thread.start()

# Start the main logging function and brightness adjustment in separate threads
if __name__ == "__main__":
    main_data_logging()
    # The file path to the Excel file should be provided here for brightness adjustment
    adjust_image_brightness("lux_data.xlsx")