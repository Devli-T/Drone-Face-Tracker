## Partial Credits: https://www.youtube.com/watch?v=rHY3T7-vK38

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 8890))

def write_yaw_to_file(yaw):
    with open("yaw_data.txt", "w") as file:
        file.write(str(yaw))

while True:
    try:
        data, server = sock.recvfrom(1024)
        status = data.decode()
        print(f"Received: {status}")

        # Extract yaw value
        try:
            yaw = int(status.split(";")[2].split(":")[1])  # Parse yaw from status message
            write_yaw_to_file(yaw)
        except (IndexError, ValueError):
            print("Failed to parse yaw")

    except Exception as e:
        print(f"Error: {e}")
        sock.close()
        break
