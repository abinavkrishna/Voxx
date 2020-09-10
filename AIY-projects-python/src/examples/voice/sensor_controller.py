import qwiic_vl53l1x
import adafruit_vcnl4040
import busio
import board
import time
import adafruit_mcp9808
import logging
import threading
import statistics
import RPi.GPIO as GPIO

from subprocess import call
from gpiozero import LED, Button
from lighting_controller import led_controller

i2c_mutex = threading.Lock()
aplay_mutex = threading.Lock()
distance = 4000
logging.basicConfig(level=logging.DEBUG)
threshold_in_mm = 350

class ProximityController:
    """ Handles proximity control related methods """
    """ Constantly checks for proximity and greets if obstacle is closer than threshold"""
    def __init__(self):
        self.long_range = qwiic_vl53l1x.QwiicVL53L1X()
        self.long_range.sensor_init()
        self.long_range.set_distance_mode(2)
        self.long_range_queue = []
        self.long_range_data = 4000
        self.rolling_average = 4000

    """ Gets data from proximity sensor periodically, computes average, reports proximity  and updates LED brightness"""
    def get_proximity_data(self):
        global distance
        for i in range(0,5):
            i2c_mutex.acquire()
            try:
                self.long_range_data = self.long_range.get_distance()
                time.sleep(0.05)
            finally:
                i2c_mutex.release()

        while(True):
            i2c_mutex.acquire()
            try:
                self.long_range.start_ranging()
                self.long_range_data = self.long_range.get_distance()
                distance = self.long_range_data
                led_controller.greeting_effect(distance)
                self.long_range.stop_ranging()
                self.long_range_queue.append(distance)
                if len(self.long_range_queue) > 5:
                    self.long_range_queue.pop(0)
                time.sleep(0.25)
            finally:
                i2c_mutex.release()
            print("Long range data: ", str(self.long_range_data))
            #long_range_data_list.append(long_range_data)
            self.rolling_average = statistics.mean(self.long_range_queue)
            if self.rolling_average < threshold_in_mm:
                return 

    """ Unused - Get interrupt request from sensor incase of threshold crossing"""
    def check_for_proximity(self):
        GPIO.setmode(GPIO.BCM)
        interrupt_pin = 5
        GPIO.setup(interrupt_pin, GPIO.IN)
        threshold_in_mm = 200
        Window = 0 #Check for proximity under threshold_in_mm
        GPIO.setup(interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        long_range = qwiic_vl53l1x.QwiicVL53L1X()
        long_range.sensor_init()
        #long_range.set_distance_threshold(ThreshLow=threshold_in_mm,ThreshHigh = 400, Window=0, IntOnNoTarget=1)
        #long_range.set_interrupt_polarity(0)
        long_range.start_ranging()
        while(True):
            button_press = GPIO.input(interrupt_pin)
            print("button state: " + str(button_press))
            if (button_press == False):
                print("Proximity detected!")
                long_range.stop_ranging()
                break

class TemperatureSensor:
    """Handles temp sense data"""
    def check_for_temperature():
        temperature_sensor = busio.I2C(board.SCL, board.SDA)
        i2c_mutex.acquire()
        try:
            temperature_data = adafruit_mcp9808.MCP9808(temperature_sensor)
        finally:
            i2c_mutex.release()
        print("Current temperature = " + str(temperature_data.temperature) + "deg C")
        time.sleep(0.1)
            #return temperature_data.temperature

class ShutdownController:
    """ Takes care of shutdown related functions"""
    def shutdown_monitor():
        power_off_button = Button(4)
        power_off_button.wait_for_press()
        logging.info("Shutdown Intitated!!")
        led_controller.switch_off()
        call("sudo shutdown -h now",shell = True)

    def hard_reset():
        logging.info("Reboot initiated!!")
        call("sudo shutdown -r now",shell = True)
