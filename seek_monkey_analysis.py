#!/usr/bin/python

# This script reads the output from seek_stall.py and parses the regular stalls
# from seek stalls graphing each one separately and together.

# USAGE: python seek_monkey_analysis.py youtube_stall_output_logfile

from __future__ import print_function
import sys
import re
import pylab
import matplotlib.pyplot as plt
import collections
import os

def get_CDF_value(stall_duration, seek_stalls):
	i = 0
	while(i < len(seek_stalls)):
		if(float(seek_stalls[i][0]) >= float(stall_duration)):
			break
		i += 1
	CDF = float(i)/len(seek_stalls)
	return CDF

def is_seek_stall(clock_time_between_stalls, seek_time):
	for i in range(1,20,1):
		if(clock_time_between_stalls - (i * 30.0) < 0.4 and clock_time_between_stalls - (i * 30.0) > -0.4):
			return True
	return False

def main():
	stall_logfilename = sys.argv[1]
	time_first = 1449657531.013220
	with open(stall_logfilename) as stall_logfile:
		previous_stall_clock_time = time_first
		seek_stalls = list()
		regular_stalls = list()
		for line in stall_logfile:
			line_match_object = re.search("Stall length ([0-9]+\.[0-9]+) at frame ([0-9]+(?:\.[0-9]+)?)s before rendering frame ([0-9]+(?:\.[0-9]+)?)s at clock time ([0-9]+\.[0-9]+)" , line)
			stall_duration = line_match_object.group(1)
			stall_clock_time = line_match_object.group(4)
			clock_time_between_stalls = abs(float(stall_clock_time) - float(previous_stall_clock_time))
			if is_seek_stall(clock_time_between_stalls, 30.0):
				seek_stalls += [(stall_duration, stall_clock_time)]
				previous_stall_clock_time = stall_clock_time
			else:
				regular_stalls += [(stall_duration, stall_clock_time)]
	# for stall in regular_stalls:
	# 	print("Stall duration " + stall[0] + " Stall clock time " + stall[1])
	# print()
	# print("######################################################")
	# print()
	# for stall in seek_stalls:
	# 	print("Stall duration " + stall[0] + " Stall clock time " + stall[1])
	CDF_data_points_map = {}
	seek_stalls.sort(key=lambda tup: tup[0])
	stall_duration_x_axis_list = list()
	i = 0.0
	while(i <= 40.0):
		stall_duration_x_axis_list += [str(i)]
		i += 0.01
	CDF_data_points_list = list()
	for stall_duration in stall_duration_x_axis_list:
		CDF_data_points_list += [get_CDF_value(stall_duration, seek_stalls)]
	plt.plot(stall_duration_x_axis_list, CDF_data_points_list)
	plt.xlabel('duration before playback resumes after a seek (seconds)')
	plt.ylabel('CDF value')
	plt.ylim([-0.01, 1.05])
	plt.xlim([0.0, 40.0])
	plt.savefig("./seek_monkey_CDF.png")
	os.system('eog ./seek_monkey_CDF.png&')
	plt.clf()




if __name__ == '__main__':
  main()
