import qwiic_vl53l1x
import time
import sys

def runExample():

    print("\nSparkFun VL53L1X Example 1\n")
    mySensor = qwiic_vl53l1x.QwiicVL53L1X()
    mySensor.sensor_init()

    while True:
        try:
            mySensor.start_ranging()                         # Write configuration bytes to initiate measurement
            time.sleep(.005)
            distance = mySensor.get_distance()   # Get the result of the measurement from the sensor
            time.sleep(.005)
            mySensor.stop_ranging()

            print("Distance(mm): %s" % distance)

        except Exception as e:
            print(e)
runExample()
