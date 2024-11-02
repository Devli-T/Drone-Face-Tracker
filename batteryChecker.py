import tello as drone


drone.start()
power = drone.get_battery()
print("Power Level: ", power, "%")
drone.takeoff()
drone.land()


