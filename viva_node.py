#!/usr/bin/env python

import rospy
import time
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from rospy_tutorials.msg import Floats

#import cv2
#def image_processing(img):

#init
isrouille = 'FALSE' 
isobstacle ='FALSE'
ispathclean = 'FALSE'


def sonar_processing():
	global isrouille
	global isobstacle
	global sonar_array
	print rospy.get_name(), "Sonar_processing heard %s"%str(sonar_array)
	print(sonar_array[0])
	if sonar_array[0]<20 or sonar_array[1]<40 or sonar_array[2]<20:
		isobstacle = 'TRUE'
	else:
		isobstacle = 'FALSE'
	return isobstacle
	
def path_processing():
	global ispathclean
	global sonar_array
	print rospy.get_name(), "Path_processing heard %s"%str(sonar_array)
	print(sonar_array[0])
	if sonar_array[0]>20 and sonar_array[1]>40 and sonar_array[2]>20 :
		ispathclean = 'TRUE'
	else:
		ispathclean = 'FALSE'
	return ispathclean
	

#def path_processing():


def callback(data):
	# ici on decide qui publie cmd_vel en fct de la touche x du joystickc

	twist = Twist()	
	global isrouille 
	global isobstacle 
	global ispathclean 
	
	if data.buttons[0]<0.5 :   #lorsque x n'est pas enfonce, alors mode auto
		rospy.loginfo("AUTO MODE")
		print("isobstacle : ", isobstacle)
		print("isrouille : ", isrouille)
		print("ispathclean : ", ispathclean)
		ispathclean = 'FALSE' #init false each loop
		
		#ret, img = cap.read() 
					#isobstacle = sonar_processing() #recherche d obstacle
			#isrouille = image_process(img) #recherche de la rouille ds l'image actuelle
		
		if isrouille == 'FALSE' and isobstacle =='FALSE':
			print("FORWARD")
			twist.linear.x = 1
			twist.angular.z = 0.0
			#ret, img = cap.read() 
			isobstacle = sonar_processing() #recherche d obstacle
			#isrouille = image_processing(img) #recherche de la rouille ds l'image actuelle
			print("publish vel 0.1 0.0")
			pub.publish(twist)

		elif isrouille == 'TRUE':
			print("ROUILLE")
			twist.linear.x = 0.0
			twist.angular.z = 0.0
			rospy.loginfo("Rouille trouvee !")
			time.sleep(5)
			isrouille = 'FALSE'	
			print("publish vel 0.0 0.0")
			pub.publish(twist)		
			
		elif isobstacle == 'TRUE':
			print("OBSTACLE")
			print("Stopping Vehicle")
			twist.linear.x = 0.0
			twist.angular.z = 0.0
			pub.publish(twist)
			time.sleep(1)
			
			ispathclean == 'FALSE'
			while ispathclean == 'FALSE':
				print("publish vel 0.0 0.6")
				twist.linear.x = 0.0
				twist.angular.z = 2
				pub.publish(twist)
				print("Rotate for 1 second...")
				time.sleep(1)
				twist.linear.x = 0.0
				twist.angular.z = 0.0
				pub.publish(twist)
				print("Analysing path...")
				time.sleep(1)
				ispathclean = path_processing()
				print("Is path clean ? : ", ispathclean)
			isobstacle = 'FALSE'
			
		else:
			print("I am here")
			print("isobstacle : ", isobstacle)
			print("isrouille : ", isrouille)
			
	else :
			#sinon on utilise le joystick en mode teleop
			rospy.loginfo("MANUAL MODE")
			twist.linear.x = 4*data.axes[1]
			twist.angular.z = 4*data.axes[0]
			pub.publish(twist)
	
#def callback_sonar(data):	
	#global data_sonar
	#data_sonar = data.data
	
def callback_sonar(data):
	#print rospy.get_name(), "I heard %s"%str(data.data)
	global sonar_array
	sonar_array = data.data
	
	

def auto_mode():
	global sonar_array
	global pub
	pub = rospy.Publisher('/cmd_vel',Twist,queue_size=5)
	rospy.init_node('viva_node', anonymous=True)
	rospy.Subscriber('joy', Joy, callback)
	rospy.Subscriber('sonar', Floats, callback_sonar)
	rospy.spin()


if __name__ == '__main__':
	# initialisation
	global isrouille
	global isobstacle
	
	try :
		cap = cv2.VideoCapture(0)
		print 'Connected to camera' 
	except :
		print 'Connection to camera failed'
		print 'Please check camera wiring'
		
	print("isobstacle : ", isobstacle)
	print("isrouille : ", isrouille)	
	
	auto_mode()
