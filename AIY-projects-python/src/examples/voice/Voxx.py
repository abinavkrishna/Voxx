#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A demo of the PCH Voxx speaker."""

import argparse
import locale
import logging
import signal
import sys
import alsaaudio
import threading
import playsound
import time
import pickle

from sensor_controller import ProximityController
from sensor_controller import TemperatureSensor
from sensor_controller import ShutdownController
from voice_controller import VolumeController
from voice_controller import VoxxAssistant
from lighting_controller import LEDController
from lighting_controller import LogoController

from aiy.assistant.grpc import AssistantServiceClientWithLed
from aiy.board import Board
from rank_bm25 import BM25Okapi
import aiy.voice.tts as tts
#import mod.snowboydecoder as snowboydecoder
from rpi_ws281x import ws
from lighting_controller import led_controller


period = 30
log = logging.getLogger(__name__)
wake_words = ['hey PCH','abch','hey bch','apch','play PCH','pay PCH','hey eh']


""" Passes volume as argument"""
def volume(string):
    value = int(string)
    if value < 0 or value > 100:
        raise argparse.ArgumentTypeError('Volume must be in [0...100] range.')
    return value

def locale_language():
    language, _ = locale.getdefaultlocale()

""" Parses input arguments to the main script"""
def parse_input():
    parser = argparse.ArgumentParser(description='Voxx application.')
    parser.add_argument('--language', default=locale_language())
    parser.add_argument('--volume', type=volume, default=100)
    parser.add_argument('--model', default='Hey-PCH.pmdl')
    args = parser.parse_args()
    return args

#def wifi_checker():


""" Application starts here """
def main():

    logging.basicConfig(level=logging.DEBUG)
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))
    args = parse_input()
    shutdown_control_thread = threading.Thread(target = ShutdownController.shutdown_monitor)
    shutdown_control_thread.start()
    #try:
    voice_assistant = VoxxAssistant(Board(),args.volume,args.language)
    #except:
    #    print("No Internet!! Exiting Application!!")
    #    led_controller.blink()
    #    return
    volume_controller = VolumeController()
    """ Starts all threads to be run concurrently """
    volume_up_control_thread = threading.Thread(target = volume_controller.volume_up_control)
    volume_down_control_thread = threading.Thread(target = volume_controller.volume_down_control)
    #temperature_sensor_thread = threading.Thread(target = TemperatureSensor.check_for_temperature)
    greeting_lighting_thread = threading.Thread(target = led_controller.greeting_effect)
    volume_up_control_thread.start()
    volume_down_control_thread.start()
    #temperature_sensor_thread.start()
    #voice_assistant = VoxxAssistant(Board(),args.volume,args.language)
    while(True):
        proximity_controller = ProximityController()
        led_controller.idle_lighting() #Idle state
        proximity_controller.get_proximity_data() #Greet state initiated
        voice_assistant.greet()
        #led_controller.listening_lighting() #Listening state
        voice_assistant.start_conversation() #Thinking/Responding state
        #TemperatureSensor.check_for_temperature()
if __name__ == '__main__':
    main()




