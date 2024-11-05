## Partial Credits: https://www.youtube.com/watch?v=rHY3T7-vK38

import socket
import threading
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)
sock.bind(('', 9000))


def get_current_yaw():
    """Reads the yaw value from the shared file."""
    try:
        with open("yaw_data.txt", "r") as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        print("Yaw data not available")
        return 0  # Default to 0 if file is missing or unreadable

def reset_yaw():
    """Adjusts yaw by 30 degrees in the appropriate direction."""
    target_yaw = 19
    adjustment_amount = 30  # Fixed adjustment in degrees

    # Get the current yaw from the file
    current_yaw = get_current_yaw()

    if current_yaw < target_yaw:
        # If yaw is negative, rotate clockwise by 30 degrees
        print(f"Rotating clockwise by {adjustment_amount} degrees")
        send_command(f'cw {adjustment_amount}')
    elif current_yaw > target_yaw:
        # If yaw is positive, rotate counterclockwise by 30 degrees
        print(f"Rotating counterclockwise by {adjustment_amount} degrees")
        send_command(f'ccw {adjustment_amount}')
    else:
        print("Yaw is already close to zero, no adjustment needed.")


while True:
    try:
        msg = input('')
        if not msg:
            break
        if 'reset' in msg:
            reset_yaw()
        if 'end' in msg:
            sock.close()
            break
        
        msg = msg.encode()
        print(f"Sending message: {msg}")
        sent = sock.sendto(msg, tello_address)
    except Exception as e:
        print(f"Error: {e}")
        sock.close()
        break