import tello as drone
import cv2
import time
import threading

print("Starting drone...")
drone.start()

print("Beginning video stream...")
drone.start_video()

print("Taking off...")
drone.takeoff()

time.sleep(2)

print("Fowrard")

for i in range(20):
    drone.left(20)
    time.sleep(0.1)


print("Landing...")
drone.land()

print("Quitting...")
stop_video_feed = True
drone.stop_video()


print("Done.")


