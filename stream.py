import socket
import cv2
import numpy as np

# Tello's video streaming address
tello_video_address = 'udp://192.168.10.1:11111'

def main():
    # Create a VideoCapture object to read the stream from the Tello
    cap = cv2.VideoCapture(tello_video_address)
    
    if not cap.isOpened():
        print("Unable to open video stream from Tello")
        return
    
    print("Streaming video. Press 'q' to exit.")
    
    while True:
        # Read a frame from the video stream
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to receive frame from Tello. Exiting...")
            break
        
        # Display the resulting frame
        cv2.imshow('Tello Video Stream', frame)
        
        # Exit the streaming by pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release the VideoCapture object and close the display window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
