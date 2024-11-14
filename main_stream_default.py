import socket
import cv2
import threading
import time

# Tello setup
tello_video = cv2.VideoCapture('udp://@0.0.0.0:11111?fifo_size=5000000&overrun_nonfatal=1')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)

# Constants for movement
IDEAL_FACE_WIDTH = 120  # Target face width in pixels to maintain distance
MOVE_DISTANCE = 20  # Distance to move in cm
ROTATE_ANGLE = 10  # Angle to rotate in degrees
HORIZONTAL_THRESHOLD = 20  # Horizontal offset threshold for rotation
VERTICAL_THRESHOLD = 20  # Vertical offset threshold for up/down movement
DISTANCE_THRESHOLD = 30  # Width difference threshold for forward/backward movement

def send_command(command):
    def run():
        sock.sendto(command.encode(), tello_address)
    threading.Thread(target=run).start()

frame_skip = 3
frame_count = 0
centre_frame_x = 320 // 2
centre_frame_y = 240 // 2

while True:
    ret, frame = tello_video.read()
    if ret:
        frame = cv2.resize(frame, (320, 240))
        frame_count += 1

        if frame_count % frame_skip == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        else:
            faces = []

        if len(faces) > 0:
            # Use the first detected face to reduce processing time
            (x, y, w, h) = faces[0]
            
            # Calculate face centre
            face_centre_x = x + w // 2
            face_centre_y = y + h // 2
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Calculate offsets
            offset_x = face_centre_x - centre_frame_x
            offset_y = face_centre_y - centre_frame_y
            distance_offset = w - IDEAL_FACE_WIDTH

            # Yaw rotation (left/right) if face is horizontally offset
            if abs(offset_x) > HORIZONTAL_THRESHOLD:
                if offset_x > 0:
                    print("Yaw left 10 degrees")
                    send_command(f'cw {ROTATE_ANGLE}')
                else:
                    print("Yaw right 10 degrees")
                    send_command(f'ccw {ROTATE_ANGLE}')

            # Move up/down if face is vertically offset
            if abs(offset_y) > VERTICAL_THRESHOLD:
                if offset_y > 0:
                    print("Move down 20 cm")
                    send_command(f'down {MOVE_DISTANCE}')
                else:
                    print("Move up 20 cm")
                    send_command(f'up {MOVE_DISTANCE}')

            # Move forward/backward if face is too close/far based on width
            if abs(distance_offset) > DISTANCE_THRESHOLD:
                if distance_offset < 0:
                    print("Move forward 20 cm")
                    send_command(f'forward {MOVE_DISTANCE}')
                else:
                    print("Move backward 20 cm")
                    send_command(f'back {MOVE_DISTANCE}')

        # Display the frame with detections
        cv2.imshow('Tello', frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            send_command("land")
            break

        # Emergency stop on 'd'
        if cv2.waitKey(1) & 0xFF == ord('d'):
            send_command("emergency")
            break

# Cleanup
tello_video.release()
cv2.destroyAllWindows()
sock.close()
