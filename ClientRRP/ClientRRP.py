import socket
import json
import time
import tkinter as tk
import subprocess
from threading import Thread
import platform

# Check if running on Raspberry Pi
def check_platform():
    """
    Checks if the script is running on a Raspberry Pi.
    
    Exits the script if not running on a Raspberry Pi.
    """
if not platform.uname().node.startswith('raspberrypi'):
    print("This script can only be run on a Raspberry Pi.")
    exit()

# Function to get output from vcgencmd command
def get_vcgencmd_output(command):
    """
    Executes a vcgencmd command and returns the output.
    
    Args:
        command: The vcgencmd command to execute
        
    Returns:
        The output of the command or error message
    """
    try:
        output = subprocess.check_output(["vcgencmd", command], universal_newlines=True)  # Execute the command
        return output.strip()  # Return the output with whitespace removed
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"  # Return error message if command fails

# Function to collect data from various vcgencmd commands
def collect_data(iteration_count):
    """
    Collects data from various vcgencmd commands.
    
    Args:
        iteration_count: The current iteration count.
    
    Returns:
        A dictionary containing collected data.
    """
    data = {
        "core_temp": get_vcgencmd_output("measure_temp"),
        "arm_freq": get_vcgencmd_output("measure_clock arm"),
        "volt_core": get_vcgencmd_output("measure_volts core"),
        "mem_arm": get_vcgencmd_output("get_mem arm"),
        "mem_gpu": get_vcgencmd_output("get_mem gpu"),
        "iteration_count": iteration_count
    }
    for key, value in data.items():
        if isinstance(value, float):
            data[key] = format(value, '.1f')
    return data  # Return the collected data

# Function to send data to the server
def send_data(client_socket):
    """
    Sends data to the server repeatedly.
    
    Args:
        client_socket: The socket object for communication with the server.
        connection_label: The Tkinter label to display connection status.
        root: The main Tkinter window object
    """
    for iteration_count in range(51):  # Send data 50 times
        data = collect_data(iteration_count)  # Collect the data
        json_data = json.dumps(data)  # Convert the data to JSON format
        client_socket.send(json_data.encode('utf-8'))  # Send the JSON data to the server
        time.sleep(2)  # Wait

# Main function to set up the GUI and send data
def main():
    """
    Main function to set up the client socket, GUI, and send data to the server.
    """
    host = '10.102.13.41'  
    port = 5001

    try:
        server_socket = socket.socket()
        server_socket.connect((host, port))

        root = tk.Tk()
        root.title("Client Data Sender")

        # Set up a label for connection status
        connection_label = tk.Label(root, text="Connecting...", fg="red")
        connection_label.pack()

        # Set up an Exit button
        exit_button = tk.Button(root, text="Exit", command=root.destroy)
        exit_button.pack()

        # Start a thread to send data to the server
        thread = Thread(target=send_data, args=(server_socket,))
        thread.start()

        # Toggle connection status label
        while True:
            if thread.is_alive():
                connection_label.config(text="Connected", fg="green")
            else:
                connection_label.config(text="Disconnected", fg="red")
            root.update()
            time.sleep(1)

        root.mainloop()
    except Exception as e:
        print("An error occurred:", e)

# Main guard clause
if __name__ == "__main__":
    main()

