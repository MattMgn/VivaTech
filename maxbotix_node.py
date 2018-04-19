#!/usr/bin/python

#Name:        maxbotix_node
#Purpose:     This node provides distance values in cm from 3 Maxbotix ultrasonic via MCP 3008 from CH0 to CH2 
#Author:      Matthieu MAGNON
#Created:     May 2017
#
#Env : Python 2.7, openCV 3, ROS indigo
#-------------------------------------------------------------------------------

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import struct
import smbus
import numpy
import time
import rospy
from rospy.numpy_msg import numpy_msg
from rospy_tutorials.msg import Floats

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

#Init
us_values = [0]*3

def get_data():
	for index in range(3):
		us_values[index] = mcp.read_adc(index)*0.5
	return us_values
	
def publish_sonar_data():
	pub = rospy.Publisher('sonar', numpy_msg(Floats),queue_size=10)
	rospy.init_node('maxbotix_node', anonymous=True)
	r = rospy.Rate(10) # 10hz
	while not rospy.is_shutdown():
		try :
			data = get_data()
			if (min(data) < 25.0):
				rospy.logwarn("Sensor failure")
		except	:
			rospy.logwarn("Bytes missed")
		array = numpy.array(us_values, dtype=numpy.float32)	
		pub.publish(array)
		r.sleep()	
		

if __name__ == '__main__':
    publish_sonar_data()
    
