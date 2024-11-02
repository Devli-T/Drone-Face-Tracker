import tello as drone


drone.start()
power = drone.get_battery()
print(f"Power Level: {power}%")
drone.takeoff()
drone.land()


