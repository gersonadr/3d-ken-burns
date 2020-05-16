#!/usr/bin/env python

import torch
import torchvision

import base64
import cupy
import cv2
import flask
import getopt
import gevent
import gevent.pywsgi
import glob
import h5py
import io
import math
import moviepy
import moviepy.editor
import numpy
import os
import random
import re
import scipy
import scipy.io
import shutil
import sys
import tempfile
import time
import urllib
import zipfile

##########################################################

assert(int(str('').join(torch.__version__.split('.')[0:2])) >= 12) # requires at least pytorch version 1.2.0

torch.set_grad_enabled(False) # make sure to not compute gradients for computational performance

torch.backends.cudnn.enabled = True # make sure to use cudnn for computational performance

##########################################################

objCommon = {}

exec(open('./common.py', 'r').read())

exec(open('./models/disparity-estimation.py', 'r').read())
exec(open('./models/disparity-adjustment.py', 'r').read())
exec(open('./models/disparity-refinement.py', 'r').read())
exec(open('./models/pointcloud-inpainting.py', 'r').read())

##########################################################

arguments_strIn = './images/doublestrike.jpg'
arguments_strOut = './autozoom.mp4'
arguments_fu = ''
arguments_fv = ''
arguments_fw = ''
arguments_fh = ''
arguments_tu = ''
arguments_tv = ''
arguments_tw = ''
arguments_th = ''
arguments_steps = ''

for strOption, strArgument in getopt.getopt(sys.argv[1:], '', [ strParameter[2:] + '=' for strParameter in sys.argv[1::2] ])[0]:
	if strOption == '--in' and strArgument != '': arguments_strIn = strArgument # path to the input image
	if strOption == '--out' and strArgument != '': arguments_strOut = strArgument # path to where the output should be stored
	if strOption == '--fu' and strArgument != '': arguments_fu = strArgument # center horizontally (in pixels)
	if strOption == '--fv' and strArgument != '': arguments_fv = strArgument # center vertically (in pixels)
	if strOption == '--fw' and strArgument != '': arguments_fw = strArgument # zoom factor
	if strOption == '--fh' and strArgument != '': arguments_fh = strArgument # shift ?
	if strOption == '--tu' and strArgument != '': arguments_tu = strArgument # center horizontally (in pixels)
	if strOption == '--tv' and strArgument != '': arguments_tv = strArgument # center vertically (in pixels)
	if strOption == '--tw' and strArgument != '': arguments_tw = strArgument # zoom factor
	if strOption == '--th' and strArgument != '': arguments_th = strArgument # shift ?
	if strOption == '--steps' and strArgument != '': arguments_steps = strArgument # shift ?

# end

##########################################################

if __name__ == '__main__':
	npyImage = cv2.imread(filename=arguments_strIn, flags=cv2.IMREAD_COLOR)

	intWidth = npyImage.shape[1]
	intHeight = npyImage.shape[0]

	fltRatio = float(intWidth) / float(intHeight)

	intWidth = min(int(1024 * fltRatio), 1024)
	intHeight = min(int(1024 / fltRatio), 1024)

	npyImage = cv2.resize(src=npyImage, dsize=(intWidth, intHeight), fx=0.0, fy=0.0, interpolation=cv2.INTER_AREA)

	process_load(npyImage, {})

	# defaults
	flvCenterU = intWidth / 2.0
	flvCenterV = intHeight / 2.0
	flvShift = 100.0
	flvZoom = 1.25

	if arguments_strCenterU != '':
		flvCenterU = float(arguments_strCenterU)
	if arguments_strCenterV != '':
		flvCenterV = float(arguments_strCenterV)
	if arguments_shift != '':
		flvZoom = float(arguments_shift)
	if arguments_zoom != '':
		flvZoom = float(arguments_zoom)

	objFrom = {
		'fltCenterU': flvCenterU,
		'fltCenterV': flvCenterV,
		'intCropWidth': int(math.floor(0.97 * intWidth)),
		'intCropHeight': int(math.floor(0.97 * intHeight))
	}

	objTo = {
		'fltCenterU': int(arguments_tu),
		'fltCenterV': int(arguments_tv),
		'intCropWidth': int(arguments_tw),
		'intCropHeight': int(arguments_th)
	}

	# objTo = process_autozoom({
	# 	'fltShift': flvShift,
	# 	'fltZoom': flvZoom,
	# 	'objFrom': objFrom
	# })

	npyResult = process_kenburns({
		'fltSteps': numpy.linspace(0.0, 1.0, int(arguments_steps)).tolist(),
		'objFrom': objFrom,
		'objTo': objTo,
		'boolInpaint': True
	})

	moviepy.editor.ImageSequenceClip(sequence=[ npyFrame[:, :, ::-1] for npyFrame in npyResult + list(reversed(npyResult))[1:] ], fps=25).write_videofile(arguments_strOut)
# end