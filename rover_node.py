#!/usr/bin/env python
#
#Name:        rover_node
#Purpose:     Script running on Rusty robot (Raspberry Pi 3). Sent GPIO to motor control board from cmd_vel, and start camera streaming
#Author:      Matthieu MAGNON
#Created:     May 2017
#
#Env : Python 2.7, openCV 3, ROS indigo
#-------------------------------------------------------------------------------



import time
import RPi.GPIO as GPIO
import roslib;
import rospy
from geometry_msgs.msg import Twist

def callback(msg):
	#rospy.loginfo("Received a /cmd_vel message!")
	#rospy.loginfo("Linear Components: [%f, %f, %f]"%(msg.linear.x, msg.linear.y, msg.linear.z))
	#rospy.loginfo("Angular Components: [%f, %f, %f]"%(msg.angular.x, msg.angular.y, msg.angular.z))

	vel_lin = msg.linear.x * 0.6
	vel_ang = msg.angular.z * 0.6
	if vel_lin>0.3:
		#AVANCE
		rospy.loginfo("Avance")
		GPIO.output(in1, 0)   #1:HIGH 0:LOW
		GPIO.output(in2, 1)   #1:HIGH 0:LOW
		GPIO.output(in3, 0)   #1:HIGH 0:LOW
		GPIO.output(in4, 1)   #1:HIGH 0:LOW
	elif vel_lin<-0.3:
		rospy.loginfo("Recule")
		GPIO.output(in1, 1)   #1:HIGH 0:LOW
		GPIO.output(in2, 0)   #:HIGH 0:LOW
		GPIO.output(in3, 1)   #1:HIGH 0:LOW
		GPIO.output(in4, 0)   #1:HIGH 0:LOW
	elif vel_lin<0.3 and vel_lin>-0.3 and vel_ang>0:
		rospy.loginfo("Tourne droite ")
		GPIO.output(in1, 1)   #1:HIGH 0:LOW
		GPIO.output(in2, 0)   #:HIGH 0:LOW
		GPIO.output(in3, 0)   #1:HIGH 0:LOW
		GPIO.output(in4, 1)   #1:HIGH 0:LOW
	elif vel_lin<0.3 and vel_lin>-0.3 and vel_ang<0:
		rospy.loginfo("Tourne gauche ")
		GPIO.output(in1, 0)   #1:HIGH 0:LOW
		GPIO.output(in2, 1)   #:HIGH 0:LOW
		GPIO.output(in3, 1)   #1:HIGH 0:LOW
		GPIO.output(in4, 0)   #1:HIGH 0:LOW	
	
	
	v_l = abs(vel_lin + vel_ang) * 100/4
	v_r = abs(vel_lin - vel_ang) * 100/4
	#v_l = abs(vel_lin * 100/4)
	#v_r = abs(vel_lin * 100/4)
	rospy.loginfo("Left Wheel,  Right Wheel: [%f, %f]"%(v_l,v_r))
	pA.ChangeDutyCycle(v_l)
	pB.ChangeDutyCycle(v_r)
	time.sleep(0.1)


def cmd_listener():
    rospy.init_node('cmd_vel_listener')
    rospy.Subscriber("/cmd_vel", Twist, callback, queue_size=2)
    rospy.spin()
    
def launch_stream():
	rospy.wait_for_service('/camera/start_capture')
	try:	
		rospy.ServiceProxy('/camera/start_capture',True)
	except rospy.ServiceException, e:
		print "Service call failed: %s"%e

if __name__ == '__main__':
	#setup
	
	enA = 18
	in1 = 23
	in2 = 24

	#motor right
	in3 = 22
	in4 = 27
	enB = 17
	
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(enA, GPIO.OUT)
	GPIO.setup(in1, GPIO.OUT)
	GPIO.setup(in2, GPIO.OUT)
	GPIO.setup(in3, GPIO.OUT)
	GPIO.setup(in4, GPIO.OUT)
	GPIO.setup(enB, GPIO.OUT)
	pA = GPIO.PWM(enA, 50) 
	pB = GPIO.PWM(enB, 50)
	pA.start(0)
	pB.start(0)

	
	cmd_listener()
	launch_stream()
