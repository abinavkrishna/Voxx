import alsaaudio
import time
import subprocess
import pickle
import logging
import threading

import RPi.GPIO as GPIO
import aiy.voice.tts as tts

#from aiy.voice.tts import thinking
from gpiozero import LED, Button
from aiy.voice.audio import play_wav,aplay,play_wav_async
from aiy.assistant.grpc import AssistantServiceClientWithLed
from aiy.board import Board
from rank_bm25 import BM25Okapi

from aiy.assistant.grpc import AssistantServiceClientWithLed
#import aiy.voice.tts
GPIO.setmode(GPIO.BCM)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(5,GPIO.OUT)

import lighting_controller
from sensor_controller  import aplay_mutex

""" Add more wake-words to the list below as required """
wake_words = ['hey PCH','abch','hey bch','apch','play PCH','pay PCH','PCH','hello PCH', 'hey eh']

class VolumeController:
    """ Provides two separate methods for volume control to be called from main application"""

    def __init__ (self):
        self.mixer = alsaaudio.Mixer('Speaker')
        self.volume_up_button = Button(17)
        self.volume_down_button = Button(27)

    def set_volume(self,volume):
        self.mixer.setvolume(volume)

    def get_volume(self):
        #mixer = alsaaudio.Mixer('Speaker')
        current_volume = self.mixer.getvolume()
        return current_volume

    """ Method for volume up control """
    def volume_up_control(self):
        while(True):
            logging.info('Press volume up/down buttons to change volumes') #Uncomment this when using buttons
            self.volume_up_button.wait_for_press() #Uncomment this when using buttons
            #GPIO.output(22,GPIO.HIGH)
            self.volume_up_button.wait_for_release()
            #GPIO.output(22,GPIO.LOW)
            #mixer = alsaaudio.Mixer('Speaker')
            current_volume = self.mixer.getvolume()
            self.mixer.setvolume(min(current_volume[0] + 10,100)) #Different volume control methodology
            logging.info(str(self.mixer.getvolume()[0]))
            if(aplay_mutex.locked() == False):
                aplay_mutex.acquire()
                try:
                    subprocess.run(["aplay","-D","default","-v","blop.wav"])
                finally:
                    aplay_mutex.release()
            else:
                logging.info("Mutex locked")

    """ Method for volume down control """
    def volume_down_control(self):
        while(True):
            logging.info('Press volume up/down buttons to change volumes \n') #Uncomment this when using buttons
            self.volume_down_button.wait_for_press() #Uncomment this when using buttons
            #GPIO.output(5,GPIO.HIGH)
            self.volume_down_button.wait_for_release()
            #GPIO.output(5,GPIO.LOW)
            #mixer = alsaaudio.Mixer('Speaker')
            current_volume = self.mixer.getvolume()
            self.mixer.setvolume(max(current_volume[0] - 10,0)) #Different volume control methodology
            logging.info(str(self.mixer.getvolume()[0]))
            if(aplay_mutex.locked() == False):
                aplay_mutex.acquire()
                try:
                    subprocess.run(["aplay","-D","default","-v","blop.wav"])
                finally:
                    aplay_mutex.release()
            else:
                logging.info("Mutex locked")

class VoxxAssistant:
    """ VoxxAssistant class acts as the voice assistant to interact with the user and respond ot queries if they
        are present in the database"""

    """@params: Board,volume,laguage - args passed from main application"""
    def __init__ (self,Board,volume,language):

        """To the user after a 10 min interval to avoid frequent triggers"""
        self.greet_timer_start = 0
        self.greet_timer_end = 0
        self.greet_timer_threshold = 600

        """For timeout from greet to idle"""
        self.greet_start_time = 0
        self.greet_end_time = 0

        """For timeout form listening to idle"""
        self.listen_start_time = 0
        self.listen_end_time = 0

        """Voice assistant"""
        self.mixer = alsaaudio.Mixer('Speaker')
        self.assistant = AssistantServiceClientWithLed(board=Board,volume_percentage=volume,language_code=language)

    """ Voxx greets the user if they approach """
    def greet(self):
        self.greet_timer_end = time.time()
        if(self.greet_timer_end - self.greet_timer_start > self.greet_timer_threshold):
            aplay_mutex.acquire()
            try:
                tts.say('Hello there!')
            finally:
                self.greet_timer_start = time.time()
            aplay_mutex.release()

    """ Looks for a list of wake words to enable conversation """
    def detect_wakeword(self):
        self.greet_start_time = time.time()
        user_text = ""
        while (True):
            self.greet_end_time = time.time()
            if(self.greet_end_time - self.greet_start_time >= 30):
                break
            try:
                user_text = self.assistant.conversation()
            except KeyboardInterrupt:
                lighting_controller.led_controller.switch_off()
                break
            except Exception:
                print("Internet out!!")
                lighting_controller.led_controller.blink()
            print('user_text is :',user_text)
            if(user_text in wake_words):
                aplay_mutex.acquire()
                try:
                    logging.info("Locking in acknowledge fn")
                    play_wav("ding.wav")
                finally:
                    aplay_mutex.release()
                    logging.info("Releasing in acknowledge fn")
                    user_text = ""
                    lighting_controller.led_controller.listening_lighting() #Listening lighting start
                    break
            elif user_text != "":
                aplay_mutex.acquire()
                try:
                    logging.info("Try again!")
                    tts.say('Sorry, could not pick that up')
                    self.greet_start_time = time.time()
                finally:
                    aplay_mutex.release()

    """ Starts conversation with Voxx after wake word detection. Timeout methodology to be decided!! """
    def start_conversation(self):
        database = open("responses.pkl")
        with open('responses.pkl','rb') as file:
            database = pickle.load(file)
        while True:
            self.listen_start_time = time.time()
            user_text = ""
            logging.info('Speak hotword to start conversation')
            volumes = self.mixer.getvolume()
            print('Volume = ' + str(volumes[0]))
            self.detect_wakeword()
            self.listen_end_time = time.time()
            if(self.listen_end_time - self.listen_start_time >=120 or self.greet_end_time - self.greet_start_time >=30):
                break
            logging.info('Ask any question to Voxx! Conversation started!')
            #user_text = self.assistant.conversation()
            try:
                for i in range(0,2):
                    user_text = self.assistant.conversation()
                    if user_text != "":
                        break
            except Exception:
                print("Internet out!!")
                lighting_controller.led_controller.blink()

            """Starts lighting effects thread"""
            if user_text != "" :
                breathing_thread = threading.Thread(target = lighting_controller.led_controller.breathing_effect)
                thinking_thread = threading.Thread(target = lighting_controller.led_controller.wave_effect)
                breathing_thread.start()
                thinking_thread.start()
            time.sleep(1)
            if (user_text.lower() in database.keys()):
                try:
                    aplay_mutex.acquire()
                    tts.say(database[user_text.lower()])
                    lighting_controller.led_controller.greeting_effect(0)
                finally:
                    aplay_mutex.release()
                    logging.info("Releasing in answer")
            elif user_text != "":
                try:
                    aplay_mutex.acquire()
                    tts.say('Sorry, I do not know the answer to that')
                    lighting_controller.led_controller.greeting_effect(0)
                finally:
                    aplay_mutex.release()
                    logging.info("Releasing in answer")

            logging.info(user_text)
            time.sleep(0.01)
