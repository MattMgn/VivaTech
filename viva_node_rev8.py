#!/usr/bin/env python
#
#Name:        optical_flow
#Purpose:     get visual odometrey from camera pointing down and rangefinder values
#Author:      Matthieu MAGNON
#Created:     May 2017
#
#Env : Python 2.7, openCV 3, ROS indigo
#-------------------------------------------------------------------------------

## added features : ##
# activate isCorrosion on edge rising

import rospy
import time
import sys
import numpy as np
import cv2
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from rospy_tutorials.msg import Floats
from sensor_msgs.msg import LaserScan 
from std_msgs.msg import Bool

## PARAMETERS

ang_min = -45 # min angular value of lidarlaser range
ang_max = 45 # max angular value of lidar laser range
nb_segment = 10 # nb of segment in the range
len_segment = (abs(ang_min) + abs(ang_max) )/ nb_segment # nb of value in each range
dist_treshold = 0.6 # min distance for abstcale detection in meter
if not isinstance(len_segment, int): # to avoid float type for len_segment
	len_segment = int(len_segment +1 )


## GLOBAL VARIABLES
switch_mode = 'DEF'
previous_mode = 'AUTO'
sonar_array = [0 for i in range(3)]
laser_array = [0 for j in range(360)]
filt_laser_array = [ 0 for j in range (nb_segment)]
inf = float('inf')
coef_vel_ang = 0.5
coef_vel_lin = 0.5
isObstacle = 'FALSE'
isCorrosion = 'FALSE'
previousCorrosionState = 'FALSE'


## MODE

def auto_mode(dist_treshold):
	global sonar_array
	global previous_mode
	global filt_laser_array
	global isObstacle
	global isCorrosion
	global coef_vel_ang
	global coef_vel_lin
	global image_np
	global previousCorrosionState
	
	# go straigh forward
	#twist.linear.x = 1.6
	#twist.angular.z = 0.0
	
	# Rising Edge
	currentCorrosionState = isCorrosion
	
	#check for obstacle under dist_treshold
	if min(filt_laser_array)<dist_treshold:
		isObstacle = 'TRUE'
	else:
		isObstacle = 'FALSE'
			
	# REACTION
	if 	isObstacle == 'TRUE':
			
		#brake rover	
		#twist.linear.x = -coef_vel_lin*1.2
		#twist.angular.z = coef_vel_ang*0.0
		#pub.publish(twist)
		
		# stop rover
		twist.linear.x = coef_vel_lin*0.0
		twist.angular.z = coef_vel_ang*0.0
		pub.publish(twist)
		
		# detect obstacle
		obst_dist = min(filt_laser_array)
		segment_nb = filt_laser_array.index(min(filt_laser_array))
		rospy.loginfo("Obstacle found in segment %s, at distance %s cm ", segment_nb+1, round(obst_dist*100,1))
		
		# compute rotation
		rot_time = compute_rotation_time(segment_nb, obst_dist)
		
		#rotate
		twist.linear.x = coef_vel_lin*0.0
		twist.angular.z = np.sign(rot_time)*coef_vel_ang*4.0
		pub.publish(twist)
		rospy.loginfo("Rotating for %s seconds ", abs(rot_time))
				
	elif currentCorrosionState != previousCorrosionState and currentCorrosionState == 'TRUE':
	#elif isCorrosion == 'TRUE':

		# stop rover
		twist.linear.x = coef_vel_lin*0.0
		twist.angular.z = coef_vel_ang*0.0
		pub.publish(twist)
				
		# display
		rospy.loginfo("Corrosion found ! ")
		time.sleep(2.0)
		
		previous_mode = 'SMTHG'
		
		# update rising edge
		previousCorrosionState = currentCorrosionState
		
	else : # go straigh forward
		twist.linear.x = coef_vel_lin*1.6
		twist.angular.z = coef_vel_lin*0.0
		pub.publish(twist)
	

def compute_rotation_time(segment_nb, obst_dist):
	global nb_segment
	global dist_treshold
	
	#define time of rotation
	rot_time = 1.5 - (1.5-0.5)/dist_treshold*obst_dist #based on obst_dist
	print('segment nb : ', segment_nb)
	rot_time = 1.5 - (1.5-0.5)/(nb_segment/2)*abs(segment_nb-nb_segment/2) #based on segment_nb
	#rot_time = 1.5 - (1.5-0.5)/(nb_segment/2)*(segment_nb-nb_segment/2)
	
	#define sense of rotation
	central_segment = nb_segment/2
	if segment_nb<central_segment: #turn right
		rot_time = abs(rot_time)
	
	else: #turn left	
		rot_time = -abs(rot_time)
		
	#print('rot_time ',rot_time)
	
	return rot_time
	
	
## CALLBACKS	

def callback_joy(data):
	global sonar_array
	global laser_array	
	global switch_mode
	global previous_mode
	global coef_vel_ang
	global coef_vel_lin
	
	if data.buttons[0]<0.5 :
		switch_mode = 'AUTO'
	else:
		switch_mode = 'MANUAL'
		twist.linear.x = coef_vel_lin * 4*data.axes[1]
		twist.angular.z = coef_vel_ang * 4*data.axes[0]
		pub.publish(twist)
		
	current_mode = switch_mode
	if current_mode != previous_mode:
		log_msg = "MODE " + switch_mode
		rospy.loginfo(log_msg)
		previous_mode = current_mode
        
		
def callback_sonar(data):
	global sonar_array
	global laser_array		
	sonar_array = data.data
	#some data filtering and processing


def callback_img(img):
	global image_np
	#print('img type ', type(img.data))
	#get compressed image and convert it to np array
	np_arr = np.fromstring(img.data, np.uint8)
	image_np = cv2.imdecode(np_arr, 1)
	

def callback_laser(scan):
	global sonar_array
	global filt_laser_array
	laser_array = scan.ranges
	
	# shit array to 90 deg
	npar = np.asarray(laser_array)
	nparr = np.roll(npar,90)
	rolled_array = [ round(elem,2) for elem in nparr] 	
	
	# data filtering
	filt_laser_array = laser_pre_processing(rolled_array, nb_segment)
	
	
def callback_bool(boole):
	global isCorrosion
	
	if boole.data == 1:
		isCorrosion = 'TRUE'
	else:
		isCorrosion = 'FALSE'
	
def laser_pre_processing(laser_array, nb_segment):		
	idx = abs(ang_min)
	while idx < abs(ang_min) + abs(ang_max):
		for j in range(nb_segment):
			nb = 0
			current_filt_laser_array = [ 0 for i in range(len_segment)] 
			for i in range (len_segment):
				# remove 'inf' values
				if laser_array[idx] != inf:
					current_filt_laser_array[i] = laser_array[idx]
					nb = nb +1
				idx = idx + 1 
			if nb != 0:
				# compute avg on each segment
				filt_laser_array[j] = sum(current_filt_laser_array)/nb
			else:
				# if empty segment force 10.0
				filt_laser_array[j] = 10.0	
		return filt_laser_array


if __name__ == '__main__':
	
	# variables
	global switch_mode
	global sonar_array
	global laser_array		
	global ang_min
	global ang_max
	global nb_segment
	global len_segment
	global dist_treshold
	global filt_laser_array
	global coef_vel_ang
	global coef_vel_lin
	global dist_treshold
	
	## initialisation
	
	# start node 
	rospy.init_node('viva_node', anonymous=True)
	pub = rospy.Publisher('/cmd_vel',Twist,queue_size=5)
	twist = Twist()
	
	# stop
	twist.linear.x = 0.0
	twist.angular.z = 0.0
	pub.publish(twist)
	
	# subscribe to topic
	rospy.Subscriber('joy', Joy, callback_joy)
	rospy.Subscriber('sonar', Floats, callback_sonar)
	rospy.Subscriber('/scan', LaserScan, callback_laser)	
	rospy.Subscriber("/isCorrosionTopic", Bool, callback_bool,  queue_size = 1)
	rospy.loginfo("INITIALIZATION SUCCESFULL")
	rospy.loginfo("Angular range : [ %s ; %s ] deg", ang_min, ang_max)
	rospy.loginfo("Nb of angular segments for laser range : %s. Angular segment : %s deg ", nb_segment, len_segment)
	rospy.loginfo("Treshold Distance :  %s  in cm", dist_treshold*100.0)
	time.sleep(0.5)
	
	# arguments
	nb_arg = len(sys.argv) - 1
	if nb_arg == 1:
		coef_vel = int(sys.argv[1])
		rospy.loginfo("Parameter for linear and angular velocity is : %s percent", sys.argv[1])
		coef_vel_lin = coef_vel/100.0
		coef_vel_ang = coef_vel/100.0
		
	elif nb_arg == 2:
		rospy.loginfo("Parameter for linear velocity is : %s percent", sys.argv[1])
		rospy.loginfo("Parameter for angular velocity is : %s percent", sys.argv[2])
		coef_vel_lin = int(sys.argv[1])/100.0
		coef_vel_ang = int(sys.argv[2])/100.0
	
	else :
		coef_vel_lin = 81/100.0
		coef_vel_ang = 72/100.0
		rospy.loginfo("Default parameter for linear velocity is : %s percent", )
		rospy.loginfo("Default parameter for angular velocity is : %s percent", )
	
	# start	
	time.sleep(0.5)
	rospy.loginfo("To start Auto Mode, press any key on joystick")

	# loop

	while True:
		time.sleep(0.2)
		if switch_mode == 'AUTO':
			auto_mode(dist_treshold)
			

