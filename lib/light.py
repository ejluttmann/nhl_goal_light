import random
import os
import platform

if "armv" in platform.machine() :
    # import GPIO if running on RPI
    import RPi.GPIO as GPIO
else :
    # import gpio_mock if not running on RPI
    from lib import gpio_mock as GPIO


def setup():
    """ Function to setup raspberry pi GPIO mode and warnings. PIN 7 OUT and PIN 15 IN """

    # Setup GPIO on raspberry pi
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    # Tell the program you want to use pin number 7 as output
    GPIO.setup(7, GPIO.OUT)
    GPIO.output(7, True)
    # Set GPIO 15 as a PULL DOWN switch
    GPIO.setup(15, GPIO.IN, GPIO.PUD_DOWN)  # If no input button connected, comment this line out
    GPIO.add_event_detect(15, GPIO.RISING, callback=activate_goal_light, bouncetime=5000)
   


def activate_goal_light():
    """ Function to activate GPIO for goal light and Audio clip. """

    # select random audio clip
    # Set random numbers depending on number of audio clips available
    songrandom = random.randint(1, 3)
    # Set pin 7 output at high for goal light ON
    GPIO.output(7, False)
    # Prepare commande to play sound (change file name if needed)
    command_play_song = 'sudo mpg123 -q ./audio/goal_horn_{SongId}.mp3'.format(
        SongId=str(songrandom))
    # Play sound
    os.system(command_play_song)
    # Set pin 7 output at high for goal light OFF
    GPIO.output(7, True)


def cleanup():
    """ Function to cleanup raspberry pi GPIO at end of code """

    # Restore GPIO to default state
    GPIO.remove_event_detect(15) #Add to end of function
    GPIO.cleanup()
    print("GPIO cleaned!")
