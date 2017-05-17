#!/usr/bin/env python
# -*- coding: utf-8 -*-

#PKG = 'numpy_tutorial'
#import roslib; roslib.load_manifest(PKG)
import struct
import smbus
import numpy
import time
import rospy
from rospy.numpy_msg import numpy_msg
from rospy_tutorials.msg import Floats

# for RPI version 1, use "bus = smbus.SMBus(0)"
bus = smbus.SMBus(1)

# This is the address we setup in the Arduino Program
address = 0x04

def get_data():
    return bus.read_i2c_block_data(address, 0);
    
def get_float(data, index):
    bytes = data[4*index:(index+1)*4]
    return struct.unpack('f', "".join(map(chr, bytes)))[0]

def publish_sonar_data():
    pub = rospy.Publisher('sonar', numpy_msg(Floats),queue_size=10)
    rospy.init_node('talker', anonymous=True)
    r = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
		try :
			data = get_data()
		except :
			rospy.logwarn("Bytes missed")
		us_1 = get_float(data, 0)
		us_2 = get_float(data, 1)
		us_3 = get_float(data, 2)
		a = numpy.array([us_1,us_2,us_3], dtype=numpy.float32)
		#a = numpy.array([1.0, 2.1, 3.2, 4.3, 5.4, 6.5], dtype=numpy.float32)
		pub.publish(a)
		r.sleep()

if __name__ == '__main__':
    publish_sonar_data()
    
