import cv2
import numpy as np
import socket
import time

tello_video = cv2.VideoCapture('udp://@0.0.0.0:11111?fifo_size=5000000&overrun_nonfatal=1')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)

while True:
    try:
        ret, frame = tello_video.read()
        if ret:
            cv2.imshow("Tello Video Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        print(e)
        
tello_video.release()
cv2.destroyAllWindows()