#!/usr/bin/python

#Usage: python logs_plot.py logfile_path

import pylab
import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches
import os
import sys
import re

def getPlotInfo(logfile_path):
	resolution_list = []
	time_list = []
	num_bytes_list = []
	time_first = -1
	time_last = -1
	most_bytes_requested = -1
	with open(logfile_path) as f:	
		for line in f:
			resolution = re.search("[0-9]+x([0-9]+)", line)
			time = re.search("([0-9]+):([0-9]+):([0-9]+)", line)
			byte_range = re.search("([0-9]+)-([0-9]+)", line)
			resolution_list += [resolution.group(1)]
			time_sec = (int(time.group(1)) * 3600 + int(time.group(2)) * 60 + int(time.group(3)))
			time_list += [time_sec]
			if time_first == -1:
				time_first = time_sec
			time_last = time_sec
			num_bytes = int(byte_range.group(2)) - int(byte_range.group(1)) 
			num_bytes_list += [num_bytes]
			if(num_bytes > most_bytes_requested):
				most_bytes_requested = num_bytes
	return (resolution_list, time_list, num_bytes_list, time_first, time_last, most_bytes_requested)

def plotResolution(resolution_list, time_list, time_first, time_last, outputFilename):
	plt.plot(time_list, resolution_list)
	plt.xlabel('time in seconds')
	plt.ylabel('resolution')
	plt.ylim([0, 1440])
	plt.xlim([time_first - 100, time_last + 100])
	plt.savefig(outputFilename)
	os.system('eog ' + outputFilename + '&')
	plt.clf()

def plotResolutionOverlay(resolution_list1, resolution_list2, time_list1, time_list2, time_last, outputFilename):
	fig, ax = plt.subplots()
	axes = [ax, ax.twinx()]
	colors = ('Blue','Red')
	version = 0
	for a, color in zip(axes, colors):
		if(version == 0):
			a.plot(time_list1, resolution_list1, color=color)
			a.set_ylim([0, 1440])
			a.tick_params(axis='y', colors=color)
			version = 1
		if(version == 1):
			a.plot(time_list2, resolution_list2, color=color)
			a.set_ylim([0, 1440])
			a.tick_params(axis='y', colors=color)
	axes[0].set_xlabel('time in seconds')
	ax.set_xlim([-100, time_last + 100])
	ax.set_ylabel('resolution')
	blue_patch = mpatches.Patch(color='blue', label='Trial 3')
	red_patch = mpatches.Patch(color='red', label='Trial 4')
	plt.legend(handles=[blue_patch, red_patch])
	plt.savefig(outputFilename)
	os.system('eog ' + outputFilename + '&')
	plt.clf()

def main():
	plotTuple1 = getPlotInfo(sys.argv[1])
	plotTuple2 = getPlotInfo(sys.argv[2])
	resolution_list1 = plotTuple1[0]
	resolution_list2 = plotTuple2[0]
	time_list1 = plotTuple1[1]
	time_list2 = plotTuple2[1]
	time_first1 = plotTuple1[3]
	time_first2 = plotTuple2[3]
	time_last1 = plotTuple1[4]
	time_last2 = plotTuple2[4]
	time_last_adjusted1 = time_last1 - time_first1
	time_last_adjusted2 = time_last2 - time_first2
	time_last_final = time_last_adjusted1 if (time_last_adjusted1 > time_last_adjusted2) else time_last_adjusted2
	time_list_adjusted1 = []
	time_list_adjusted2 = []
	for i in range(0, len(time_list1)):
		time_list_adjusted1 += [time_list1[i] - time_first1]
	for i in range(0, len(time_list2)):
		time_list_adjusted2 += [time_list2[i] - time_first2]
	plotResolutionOverlay(resolution_list1, resolution_list2, time_list_adjusted1, time_list_adjusted2, time_last_final, "./resolution_overlay.png")
	plotResolution(resolution_list1, time_list_adjusted1, 0, time_last_final, "./resolution1.png")
	plotResolution(resolution_list2, time_list_adjusted2, 0, time_last_final, "./resolution2.png")



if __name__ == '__main__':
  main()