import tkinter as tk
from threading import Thread
import socket
import json
import time

window_open = True

def blink_led(led_label):
    """
    Blink the LED label by changing its color to green for 1 second.

    Args:
        led_label: The Tkinter Label widget representing the LED.
    """
    original_color = led_label.cget("background")
    led_label.config(background="green")
    led_label.after(1000, lambda: led_label.config(background=original_color))

def update_gui(data, label, window, led_label):
    """
    Update the GUI label with new data and blink the LED.
    
    This function updates the text of the provided label with new data
    and blinks the LED label.
    
    Args:
        data: The new data to be displayed on the label.
        label: The GUI label to be updated.
        window: The main window object of the GUI.
        led_label: The label representing the LED.
    """
    global window_open
    if not window_open:
        return
    
    display_text = "\n".join(f"{key}: {value}" for key, value in data.items())
    label.config(text=display_text)

    # Blink the LED
    blink_led(led_label)

def listen_to_client(conn, label, window, led_label):
    """
    Listen to the client and update the GUI with received data.

    This function listens to data from a socket connection and updates the
    GUI based on the recieved data. The function runs in a seperate thread to
    keep the GUI responsive.
    
    Args:
        conn: The connection object to the client.
        label: The GUI label to be updated with data.
        window: The main window object of the GUI.
        led_label: The label representing the LED.
    """
    global window_open
    while window_open:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            json_data = json.loads(data)
            display_data = {k: json_data[k] for k in list(json_data)[:6]}
            if window_open:
                label.after(100, update_gui, display_data, label, window, led_label)
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)
        except Exception as e:
            print("An error occurred:", e)
    conn.close()

def main():
    """
    Main function to set up the server, GUI components, and start the
    listening thread.
    
    This function sets up a server socket to listen for incoming connections,
    intializes the GUI components, and starts a seperate thread for listening
    to clients data.
    """
    global window_open
    host = '10.102.13.41'  
    port = 5001  

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(1)

    conn, addr = server_socket.accept()

    root = tk.Tk()
    root.title("Server Data Display")

    # Set up a label for data display
    label = tk.Label(root, text="Waiting for Data...")
    label.pack()

    # Set up an LED label
    led_label = tk.Label(root, text="LED", bg="red", width=10)
    led_label.pack()
    
    def on_close():
        global window_open
        window_open = False
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Start a thread to listen to client data
    thread = Thread(target=listen_to_client, args=(conn, label, root, led_label))
    thread.daemon = True
    thread.start()

    root.mainloop()
    window_open = False

# Main guard clause
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
