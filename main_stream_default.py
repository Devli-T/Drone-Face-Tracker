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
GAIN_X = 0.5  # Horizontal movement
GAIN_Y = 0.5  # Vertical movement
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

            # Determine movement commands based on proportional control
            if abs(offset_x) > 20:  # Horizontal movement threshold
                # Rotate (yaw) instead of lateral movement for smoother tracking
                yaw_speed = int(GAIN_YAW * offset_x)
                if yaw_speed > 0:
                    print("yaw right")
                    send_command(f'cw {min(yaw_speed, 30)}')  # Rotate clockwise
                else:
                    print("yaw left")
                    send_command(f'ccw {min(-yaw_speed, 30)}')  # Rotate counterclockwise

            if abs(offset_y) > 20:  # Vertical movement threshold
                up_down_speed = int(GAIN_Y * offset_y)
                if up_down_speed > 0:
                    print("up")
                    send_command(f'up {max(up_down_speed, 20)}')
                else:
                    print("down")
                    send_command(f'down {max(-up_down_speed, 20)}')

            # Adjust forward/backward to maintain an ideal distance from face
            ideal_face_width = 120  # Target face size in pixels
            distance_offset = ideal_face_width - w

            if abs(distance_offset) > 70:  # Lowered distance threshold for better responsiveness
                forward_back_speed = max(10, int(GAIN_X * distance_offset))  # Minimum speed of 10
                if forward_back_speed > 0:
                    print("forward")
                    send_command(f'forward {max(forward_back_speed, 20)}')
                else:
                    print("back")
                    send_command(f'back {max(-forward_back_speed, 20)}')

            # Break out after handling the first detected face
            break

        # Display the frame
        cv2.imshow('Tello', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
tello_video.release()
cv2.destroyAllWindows()
sock.close()
