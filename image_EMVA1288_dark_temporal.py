#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 14:30:38 2023

@author: teledyne
"""
import subprocess
#import optimom
import v4l2
import fcntl
import mmap
import time
import api
import os

#choose resolution (select one):
api.initialize(sensor_mode=0) #10 bits
#api.initialize(sensor_mode=2) #8 bits

#setup the exposure time needed to obtain fully saturated image
exposure_max = 61000 #µs

#loop parameters
nb_steps=50 #keep this value
exposure_step=exposure_max/nb_steps #keep this value

fd = api.get_device()

print(">> get device capabilities")
cp = v4l2.v4l2_capability()
fcntl.ioctl(fd, v4l2.VIDIOC_QUERYCAP, cp)


print(">> device setup")

print(">> init mmap capture")
req = v4l2.v4l2_requestbuffers()
req.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
req.memory = v4l2.V4L2_MEMORY_MMAP
req.count = 1  # nr of buffer frames
fcntl.ioctl(fd, v4l2.VIDIOC_REQBUFS, req)  # tell the driver that we want some buffers 
print("req.count", req.count)
buffers = []

print(">>> VIDIOC_QUERYBUF, mmap, VIDIOC_QBUF")
for ind in range(req.count):
    # setup a buffer
    buf = v4l2.v4l2_buffer()
    buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    buf.memory = v4l2.V4L2_MEMORY_MMAP
    buf.index = ind
    fcntl.ioctl(fd, v4l2.VIDIOC_QUERYBUF, buf)
    mm = mmap.mmap(fd.fileno(), buf.length, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=buf.m.offset)
    buffers.append(mm)
    # queue the buffer for capture
    fcntl.ioctl(fd, v4l2.VIDIOC_QBUF, buf)

print(">> Start streaming")
buf_type = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
fcntl.ioctl(fd, v4l2.VIDIOC_STREAMON, buf_type)
time.sleep(1) #mandatory to avoid I2C write issue

def take_image(image_name):
    
    for i in range(3):
        buf = v4l2.v4l2_buffer()
        buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        buf.memory = v4l2.V4L2_MEMORY_MMAP
        fcntl.ioctl(fd, v4l2.VIDIOC_DQBUF, buf)  # get image from the driver queue
        mm = buffers[buf.index]
        mm.read(len(mm))
        mm.seek(0)
        fcntl.ioctl(fd, v4l2.VIDIOC_QBUF, buf)
    # Reactivate streaming
    with open(image_name, "wb") as binary_file:
        buf = v4l2.v4l2_buffer()
        buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        buf.memory = v4l2.V4L2_MEMORY_MMAP
        fcntl.ioctl(fd, v4l2.VIDIOC_DQBUF, buf)  # get image from the driver queue
        mm = buffers[buf.index]
        binary_file.write(mm.read(len(mm)))
        mm.seek(0)
        fcntl.ioctl(fd, v4l2.VIDIOC_QBUF, buf)

def write_file(path, filename, content):
    # write content into a file
    fname = os.path.join(path, filename)
    with open(fname, 'a') as f:
        f.write(content)
        f.write('\n')
    return fname

# EMVA1288 parameters
path = os.getcwd()
filename = "EMVA1288_Data_dark_temporal.txt"


write_file(path, filename, "#########################")
write_file(path, filename, "v 3.1")
write_file(path, filename, "n 0 1920 1080")

#write image offset
#reg_addr = 0x22
#reg_val = 20
#optimom.write_sensor_reg(i2c, reg_addr, reg_val)
#offset_reg=optimom.read_sensor_reg(i2c, reg_addr)
#print("offset_reg={} 0x{:04x}".format(offset_reg, offset_reg))

subprocess.call(['i2ctransfer -f -y 6 w3@0x10 0x22 0x00 0x20'], shell=True) #image offset
print("write")
offset=subprocess.check_output('i2ctransfer -f -y 6 w1@0x10 0x22 r2', shell=True)
print("offset_reg={}".format(offset))

for i in range(exposure_step, exposure_max, exposure_step):
    api.set_control_value("exposure",i)
    print("exposure={}us".format(int(i)))
    time.sleep(0.2)
    write_file(path, filename, "d " + str(i / 1000))  
    if (int(i / 1000) < 10):
        write_file(path, filename, "i Images\\d_00" + str(int(i / 1000)) + "_snap_000.tif")
        write_file(path, filename, "i Images\\d_00" + str(int(i / 1000)) + "_snap_001.tif")
        take_image("d_00{}_snap_000".format(int(i / 1000)) + ".raw")
        print("saved image: d_00{}_snap_000.raw".format(int(i / 1000)))
        take_image("d_00{}_snap_001".format(int(i / 1000)) + ".raw")
        print("saved image: d_00{}_snap_001.raw".format(int(i / 1000)))
    else:
        write_file(path, filename, "i Images\\d_0" + str(int(i / 1000)) + "_snap_000.tif")
        write_file(path, filename, "i Images\\d_0" + str(int(i / 1000)) + "_snap_001.tif")
        take_image("d_0{}_snap_000".format(int(i / 1000)) + ".raw")
        print("saved image: d_0{}_snap_000.raw".format(int(i / 1000)))
        take_image("d_0{}_snap_001".format(int(i / 1000)) + ".raw")
        print("saved image: d_0{}_snap_001.raw".format(int(i / 1000)))
    
  
print(">> Stop streaming")
fcntl.ioctl(fd, v4l2.VIDIOC_STREAMOFF, buf_type)
for i in buffers:
    i.close()
api.close()

  
     
