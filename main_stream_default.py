import socket
import cv2
import threading
import time

# Tello setup
tello_video = cv2.VideoCapture('udp://@0.0.0.0:11111?fifo_size=5000000&overrun_nonfatal=1')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)

# Proportional gain constants for smoother movement
GAIN_X = 0.2  # Horizontal movement
GAIN_Y = 0.2  # Vertical movement
GAIN_YAW = 0.5  # Rotation

def send_command(command):
    def run():
        sock.sendto(command.encode(), tello_address)
    threading.Thread(target=run).start()

frame_skip = 3  # Skip detection every few frames
frame_count = 0
centre_frame_x = 320 // 2  # Assuming resized frame of 320x240
centre_frame_y = 240 // 2

while True:
    # Beginning the drone
    send_command("command")
    time.sleep(1)   # Add a slight delay to be sure
    send_command("takeoff")  

    ret, frame = tello_video.read()
    if ret:
        frame = cv2.resize(frame, (320, 240))  # Resize for faster processing
        frame_count += 1

        if frame_count % frame_skip == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        else:
            faces = []

        for (x, y, w, h) in faces:
            # Calculate face centre
            face_centre_x = x + w // 2
            face_centre_y = y + h // 2
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Calculate offsets from frame centre
            offset_x = face_centre_x - centre_frame_x
            offset_y = face_centre_y - centre_frame_y


            # Adjust forward/backward to maintain an ideal distance from face
            ideal_face_width = 120  # Target face size in pixels
            distance_offset = abs(ideal_face_width - w)     # of an arbitrary unit and scale
            maybe_forward_dist = max(20, int(GAIN_X * distance_offset))


            # Set up a priority order of events:
            #   1. Move up/down
            #   2. Move left/right
            #   3. Move forward/backwards
            # Removing the 'elif's for regular if's can test if the drone can handle multiple at once.

            # Up / Down
            if abs(offset_y) > 20:  # Vertical movement threshold
                up_down_speed = max(abs(int(GAIN_Y * offset_y)), 20)    # in cm

                if offset_y > 0:
                    print("up")
                    send_command(f'up {up_down_speed}')
                else:
                    print("down")
                    send_command(f'down {up_down_speed}')

            # Left / Right
            elif abs(offset_x) > 20:  # 20 is not determined by the angle. It is an arbitrary number.
                yaw_speed = abs(int(GAIN_YAW * offset_x))
                rotation_deg = min(max(yaw_speed, 1), 30)  # Bound between 1 and 30 degrees.

                if offset_x > 0: 
                    print(f"Yaw left {rotation_deg}")
                    send_command(f'cw {rotation_deg}')
                else: 
                    print(f"Yaw right {rotation_deg}")
                    send_command(f'ccw {rotation_deg}')

            # Forward / backward + with deadzone
            elif distance_offset > 80:
                print(f"forward {maybe_forward_dist}")
                send_command(f'forward {maybe_forward_dist}')
            elif distance_offset < 60:
                print(f"back {maybe_forward_dist}")
                send_command(f'back {maybe_forward_dist}')

            # Break out after handling the first detected face
            break

        # Display the frame
        cv2.imshow('Tello', frame)

        # EXITS
        if cv2.waitKey(1) & 0xFF == ord('q'):   # Press 'q' to exit the program
            send_command("land")
            break

        if cv2.waitKey(1) & 0xFF == ord('d'):   # Press 'd' to *ABORT* the program
            send_command("emergency")
            break

# Cleanup
tello_video.release()
cv2.destroyAllWindows()
sock.close()
