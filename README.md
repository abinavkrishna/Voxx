# Voxx

Embedded Python application for raspberry pi based smart speaker

The Application is organized into multiple layers.

The lowest layer consists of the raspbian OS and low level drivers that enable communication and other peripherals.
The middle layer consists of various speech processing engines, namely Speech-to-text and Text-to-Speech engines.
The top layers consist of various device controllers which include Sensor, lighting and voice assistant controllers. 
The topmost layer of the is the main application script that coordinates between multiple lower level application modules  

A multi-threaded architecture is used, in which the main applicaiton spawns various various device controller threads and
the inter-thread synchronization is done through synchronization primitives provided by python.

Organization:
AIY-projects-python->src->examples->voice->Voxx.py => Main application
AIY-projects-python->src->examples->voice->sensor_controller.py => Sensor controller
AIY-projects-python->src->examples->voice->voice_controller.py => Voice assistant
AIY-projects-python->src->examples->voice->lighting_controller.py => Lighting controller
AIY-projects-python->src->aiy->assistant->grpc.py => Speech-to-text
AIY-projects-python->src->aiy->voice->tts.py => Text-to-Speech
