#!/usr/bin/env python
#
#Name:        rover_node
#Purpose:     This node publish battery voltage informations from 2 Li Po 3s battery via MCP 3008 from CH3 and CH4 into /battery_node topic
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
voltage_values = [0]*2

def get_data():
	for index in [3, 4]: #pin CH3 CH4
		voltage_values[index-3] = mcp.read_adc(index)*5.0/1024.0
	return voltage_values
	
def publish_battery_data():
	pub = rospy.Publisher('battery_state', numpy_msg(Floats),queue_size=10)
	rospy.init_node('battery_node', anonymous=True)
	r = rospy.Rate(0.1) # 10hz
	while not rospy.is_shutdown():
		try :
			data = get_data()
			if data[0] < 3.5:
				rospy.logwarn("Low voltage on PC battery")	
			if data[1] < 3.5:
				rospy.logwarn("Low voltage on MOTOR battery")			
		except	:
			rospy.logwarn("Bytes missed")
		array = numpy.array(voltage_values, dtype=numpy.float32)	
		pub.publish(array)
		r.sleep()	
		

if __name__ == '__main__':
    publish_battery_data()
    
