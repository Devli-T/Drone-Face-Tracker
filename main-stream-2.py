import socket
import cv2
import threading
import time

# Tello setup
tello_video = cv2.VideoCapture('udp://@0.0.0.0:11111?fifo_size=5000000&overrun_nonfatal=1')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)

def send_command(command):
    def run():
        sock.sendto(command.encode(), tello_address)
    threading.Thread(target=run).start()
    
frame_skip = 5  # Skip detection every few frames
frame_count = 0
centre_frame_x = 320 // 2  # Assuming resized frame of 320x240
centre_frame_y = 240 // 2

# Updated gain constants
GAIN_YAW = 0.2
GAIN_DISTANCE = 0.2
GAIN_LATERAL = 0.2
GAIN_VERTICAL = 0.15

ideal_face_width = 80  # Target face size in pixels


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

            # Calculate offsets
            offset_x = face_centre_x - centre_frame_x
            offset_y = face_centre_y - centre_frame_y
            distance_offset = ideal_face_width - w

            # Horizontal (yaw) adjustments
            if abs(offset_x) > 10:
                yaw_speed = int(GAIN_YAW * offset_x)
                send_command(f"{'cw' if yaw_speed > 0 else 'ccw'} {min(abs(yaw_speed), 20)}")  # Ensure min 20

            # # Vertical (up/down) adjustments with minimum threshold
            # if abs(offset_y) > 10:
            #     vertical_speed = int(GAIN_VERTICAL * offset_y)
            #     vertical_speed = max(20, abs(vertical_speed))  # Enforce minimum 20
            #     send_command(f"{'up' if vertical_speed < 0 else 'down'} {vertical_speed}")
            
            # # Forward/Backward adjustments with minimum threshold
            # if abs(distance_offset) > 10:
            #     forward_back_speed = int(GAIN_DISTANCE * distance_offset)
            #     forward_back_speed = max(20, abs(forward_back_speed))  # Ensure minimum 20
            #     send_command(f"{'forward' if forward_back_speed < 0 else 'back'} {forward_back_speed}")

            # # Horizontal (left/right) adjustments with minimum threshold
            # if abs(offset_x) > 20:
            #     lateral_speed = int(GAIN_LATERAL * offset_x)
            #     lateral_speed = max(20, abs(lateral_speed))  # Ensure minimum 20
            #     send_command(f"{'left' if lateral_speed < 0 else 'right'} {lateral_speed}")
            
            break  # Stop after first face is handled

        # Display the frame
        cv2.imshow('Tello', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
tello_video.release()
cv2.destroyAllWindows()
sock.close()
