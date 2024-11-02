import tello as drone
import cv2
import time
import threading

stop_video_feed = False
def show_drone_video_feed():
    global stop_video_feed
    while True:
        frame = drone.get_video_frame()

        if frame is None:
            print("No video feed available.")
            break

        # Display the frame in a window
        cv2.imshow('Drone Video Feed', frame)

        # Exit the video feed window if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

print("Starting drone...")
drone.start()

print("Beginning video stream...")
video_thread = threading.Thread(target=show_drone_video_feed)
video_thread.start()

print("Taking off...")
drone.takeoff()

time.sleep(5)

print("Landing...")
drone.land()

print("Quitting...")
stop_video_feed = True
video_thread.join()


print("Done.")


