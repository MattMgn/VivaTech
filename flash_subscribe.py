#!/usr/bin/env python

#Name:        flashlight
#Purpose:     Run on Rusty robot. Change PWM value to blink a BlueRobotics flashLight when /isCorrosionTopic is published
#Author:      Matthieu MAGNON
#Created:     May 2017
#
#Env : Python 2.7, openCV 3, ROS indigo
#-------------------------------------------------------------------------------

import rospy
import time
import RPi.GPIO as GPIO
from std_msgs.msg import Bool

#Parameter
gpio_pwm = 6

#global variable
flash_flag = 0


def callback_flash(msg):
	global flash_flag
	flash_flag =  msg.data
	print('flash callback', flash_flag)
	rospy.loginfo(rospy.get_caller_id() + 'I heard %s', flash_flag)

def flash():
	light.ChangeDutyCycle(100)
	#print('led on')
	time.sleep(0.2)
	light.ChangeDutyCycle(0)
	#print('led off')
	time.sleep(0.2)
	
def spinning():
	global flash_flag
	#print('flash flag', flash_flag)
	if flash_flag==1:
		flash()
		
def listener():
	rospy.init_node('flash_listener', anonymous=True) #defini le nom du node
	rospy.Subscriber('/isCorrosionTopic', Bool, callback_flash, queue_size=2) 
	#rospy.spin()
	
	
	
if __name__ == '__main__':
	global flash_flag
	
	#GPIO.cleanup()
	
	# define PWM output
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(gpio_pwm, GPIO.OUT)
	light = GPIO.PWM(gpio_pwm, 50)
	light.start(0)
	light.ChangeDutyCycle(0)

	# init
	listener()
	
	# loop
	while True:
		time.sleep(0.1)
		spinning()
		
	
	while True:
		try:
			time.sleep(0.1)
			spinning()
		except:
			light.stop(0)
			GPIO.cleanup()
		
		


