import board
import busio
#import adafruit_is31fl3731
import time
import board
import threading
import rpi_ws281x
import RPi.GPIO as GPIO
import math

#from sensor_controller import ProximityController
#from sensor_controller import i2c_mutex
from rpi_ws281x import Color, PixelStrip, ws

responding = 0
count = 0
distance = 200

LED_COUNT = 144                # Number of LED pixels
LED_PIN = 10                    # GPIO pin connected to the pixels (must suppo
LED_BRIGHTNESS = 10   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False        # True to invert the signal (when using NPN transistor level 
#LED_STRIP = ws.SK6812_STRIP_RGBW

"""
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN,GPIO.OUT)
pwm = GPIO.PWM(LED_PIN,200)
"""
class LEDController:

    def __init__(self,LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,LED_STRIP):
        self._strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,LED_STRIP)
        self._strip.begin()
        self._step = 0.5
        self._start = 0

    def color_wipe(self,color,wait_ms=50):
        for i in range(self._strip.numPixels()):
            self._strip.setPixelColor(i, color)
            time.sleep(wait_ms / 1000.0)
        self._strip.show()
            #time.sleep(wait_ms / 1000.0)

    def idle_lighting(self):
        self.color_wipe(Color(50,50,50),0)

    def listening_lighting(self):
        #proximity = ProximityController.get_proximity_data()
        self.color_wipe(Color(150,150,150),0)

    def map_range(self,x, inLow, inHigh, outLow, outHigh):
        inRange = inHigh - inLow
        outRange = outHigh - outLow
        inScale = (x - inLow)/inRange
        return outLow + (inScale * outRange)

    def breathing_effect(self):
        while responding:
            duty = self.map_range(math.sin(self._start),-1,1,0,150)
            self._start += self._step
            #self.color_wipe(Color(0,0,0,int(duty)),0)
            self.color_wipe(Color(int(duty),int(duty),int(duty)),0)
            time.sleep(0.05)

    def alternate_lighting(self,color,wait_ms=50):
        for i in range(0,self._strip.numPixels(),2):
            self._strip.setPixelColor(i, color)
            time.sleep(wait_ms / 1000.0)
        self._strip.show()
        time.sleep(1)

    def greeting_effetct(self):
        brightness = self.map_range(-distance,-4000,0,0,150)
        self.color_wipe(Color(int(brightness),int(brightness),int(brightness),0),0)

    def wave_effect(self,color=Color(50,50,50),wait_ms=5):
        for i in range(0,self._strip.numPixels(),5):
            self.switch_off()
            for j in range(0,5):
                self._strip.setPixelColor(i+j, color)
                time.sleep(wait_ms / 1000.0)
            self._strip.show()

        for i in range(self._strip.numPixels(),-1,-5):
            self.switch_off()
            for j in range(0,min(5,i)):
                self._strip.setPixelColor(i-j, color)
                time.sleep(wait_ms / 1000.0)
            self._strip.show()

    def switch_off(self):
        self.color_wipe(Color(0,0,0),0)

#while True:
#led.idle_lighting()
#LEDController.color_wipe(strip, Color(0,50,0,0),0)    # White
#time.sleep(2)
#LEDController.color_wipe(strip, Color(0,150,0,0),0)
led_controller = LEDController(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,LED_STRIP)
led_controller.idle_lighting()
#led_controller.breathing_effect()
#led_controller.alternate_lighting(Color(50,50,50,0),0)
#led_controller.switch_off()
#led_controller.wave_effect(Color(50,50,50,0),0)
