import board
import busio
import adafruit_is31fl3731
import time
import threading
import rpi_ws281x
import RPi.GPIO as GPIO
import math

import aiy.voice.tts as tts
from rpi_ws281x import Color, PixelStrip, ws

LED_COUNT = 58               # Number of LED pixels
LED_PIN = 10                    # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000    # LED signal frequency in hertz (usual
LED_DMA = 10                    # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 125   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False        # True to invert the signal (when using NPN transistor level 
LED_CHANNEL = 0
#LED_STRIP = ws.SK6812_STRIP_RGBW
#LED_STRIP = ws.SK6812W_STRIP
LED_STRIP = ws.WS2811_STRIP_GBR

class LogoController:
    """ Alternate logo lighting controller - not used"""
    def power_up_logo():
        matrix = adafruit_is31fl3731.Matrix()
        matrix.fill(brightness =10)

class LEDController:

    """ Takes care of lighting effects for Voxx

    @params: LED_COUNT: Number of LEDs to light up
             LED_PIN  : Which pin LED is connected to
             LED_FREQ_HZ: Signal frequency in Hz
             LED_DMA: DMA channel for generating the signal - defaults to 10
             LED_INVERT: Option to invert signal. Default False
             LED_BRIGHTNESS: Max brightness of LEDs - set to 10. Max 255
             LED_CHANNEL: Defaults to 0
             LED_STRIP: LED strip type. 'ws.WS2811_STRIP_RGB' to be used for Voxx
    """
    def __init__(self,LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,LED_STRIP):
        self._strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,LED_STRIP)
        self._strip.begin()
        self._step = 0.5
        self._start = 0

    """Sets all pixels to 'color - Color(R,G,B)' color given by RGB values from 0-255"""
    def color_wipe(self,color,wait_ms=50):
        for i in range(0,self._strip.numPixels()):
            self._strip.setPixelColor(i, color)
            time.sleep(wait_ms / 1000.0)
        self._strip.show()
            #time.sleep(wait_ms / 1000.0)

    """ Minimum brightness idle state lighting"""
    def idle_lighting(self):
        self.color_wipe(Color(50,50,50),0)

    """ Maximum brightness listening state lighting"""
    def listening_lighting(self):
        #proximity = ProximityController.get_proximity_data()
        self.color_wipe(Color(255,255,255),0)

    """ Maps 'x' in input range to output range """
    def map_range(self,x, inLow, inHigh, outLow, outHigh):
        inRange = inHigh - inLow
        outRange = outHigh - outLow
        inScale = float(x - inLow)/float(inRange)
        return outLow + (inScale * outRange)
    """
    # Alternate breathing effect if signalling does not work
    def breathing_effect(self):
        self._start = 0
        has_responded = 0
        while True:
            if tts.responding:
                duty = self.map_range(math.sin(self._start),-1,1,0,255)
                self._start += self._step
                #self.color_wipe(Color(0,0,0,int(duty)),0)
                self.color_wipe(Color(int(duty),int(duty),int(duty)),0)
                time.sleep(0.05)
                has_responded = 1

            elif has_responded:
                break
            time.sleep(0.1)
    """

    """ Breathing effect for response state lighting"""
    def breathing_effect(self):
        self._start = 0
        tts.response_available.wait()
        print("response lighting")
        while tts.responding:
        #while True:
            duty = self.map_range(math.sin(self._start),-1,1,0,200)
            self._start += self._step
            #self.color_wipe(Color(0,0,0,int(duty)),0)
            self.color_wipe(Color(int(duty),int(duty),int(duty)),0)
            time.sleep(0.2)

    """ Lights up alternate LEDs """
    def alternate_lighting(self,color,wait_ms=50):
        for i in range(0,self._strip.numPixels(),2):
            self._strip.setPixelColor(i, color)
            time.sleep(wait_ms / 1000.0)
        self._strip.show()
        time.sleep(1)

    """ Maps user distance to light intensity """
    def greeting_effect(self,distance):
        if(distance > 2500):
            brightness = 50
        else:
            brightness = self.map_range(-distance,-2500,0,50,200)
        print(str(brightness))
        #time.sleep(0.1)
        self.color_wipe(Color(int(brightness),int(brightness),int(brightness)),0)

    """ Indicates unavailability of internet """
    def blink(self):
        while(True):
            self.color_wipe(Color(50,50,50),0)
            time.sleep(1)
            self.color_wipe(Color(0,0,0),0)
            time.sleep(1)

    """ Wave effect to convey that Voxx is 'thinking' """
    def wave_effect(self,color=Color(255,255,255),wait_ms=5):
        while tts.thinking:
            for i in range(0,self._strip.numPixels(),5):
                if(tts.thinking == 0):
                    break
                self.switch_off()
                for j in range(0,10):
                    self._strip.setPixelColor(i+j, color)
                    time.sleep(wait_ms / 1000.0)
                self._strip.show()

            for i in range(self._strip.numPixels(),-1,-5):
                if(tts.thinking == 0):
                    break
                self.switch_off()
                for j in range(0,min(10,i)):
                    self._strip.setPixelColor(i-j, color)
                    time.sleep(wait_ms / 1000.0)
                self._strip.show()
            time.sleep(0.1)

    def switch_off(self):
        self.color_wipe(Color(0,0,0),0)


""" LED strip object to be used from sensor_controller and main application"""
led_controller = LEDController(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,LED_STRIP)
#led_controller.idle_lighting()
#led_controller.listening_lighting()
#led_controller.breathing_effect()
#led_controller.alternate_lighting(Color(50,50,50),0)
#led_controller.switch_off()
#led_controller.wave_effect(Color(50,50,50,0),0)
