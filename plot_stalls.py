#!/usr/bin/python

# This script reads the log file from mm-youtubereplay (youtube_replay.py) 
# and outputs stall data for the given video trial.

# USAGE: python plot_stalls.py youtube_stall_logfile

from __future__ import print_function
import sys
import re
from decimal import *
import pylab
import matplotlib.pyplot as plt 
import collections
import os

def main():
	stall_logfilename = sys.argv[1]
	filename_match_object = re.search("youtube_stall_logs/(.+).txt", stall_logfilename)
	stall_data_filename = "./youtube_stall_logs/" + filename_match_object.group(1) + "_stall_data.txt"
	stall_data_file = open(stall_data_filename, 'w')
	frame_list = list()
	frame_set = set()
	stall_dict = collections.defaultdict(lambda: Decimal(0.0))
	with open(stall_logfilename) as stall_logfile:
		previous_render_call_time = Decimal(0.0)
		previous_frame_presentation_time = ""
		for line in stall_logfile:
			match_object = re.search("RENDER CALL ON: ([0-9]+(?:\.[0-9]+)?)s TIME: (.+)", line)
			if match_object:
				render_call_time = Decimal(match_object.group(2))
				frame_presentation_time = match_object.group(1)
				if not frame_presentation_time in frame_set: 
					frame_list += [frame_presentation_time]
					frame_set.add(frame_presentation_time)
				if previous_render_call_time == 0:
					previous_render_call_time = render_call_time
					previous_frame_presentation_time = frame_presentation_time
				if render_call_time - previous_render_call_time > 0.018: #render calls occur every 17milliseconds or so
					stall_dict[previous_frame_presentation_time] += render_call_time - previous_render_call_time - Decimal(0.017)
					print("Stall length " + str(render_call_time - previous_render_call_time) + " at frame " + str(previous_frame_presentation_time) + "s", file=stall_data_file)
				previous_render_call_time = render_call_time
				previous_frame_presentation_time = frame_presentation_time
	final_stalls_length_list = list()
	for frame in frame_list:
		if frame in stall_dict:
			final_stalls_length_list += [stall_dict[frame]]
		else: 
			final_stalls_length_list += [0.0]
	final_frame_list = list()
	time_last = 0.0
	for frame in frame_list:
		final_frame_list += [float(frame)]
		time_last = float(frame)
	plt.plot(final_frame_list, final_stalls_length_list)
	plt.xlabel('time in video in seconds')
	plt.ylabel('stall duration in seconds')
	plt.ylim([-2, 20])
	plt.xlim([-100, time_last + 100])
	plt.savefig("./stalls.png")
	os.system('eog ./stalls.png&')
	plt.clf()

if __name__ == '__main__':
  main()