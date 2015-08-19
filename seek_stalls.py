#!/usr/bin/python

# This script reads the log file from mm-youtubereplay (youtube_replay.py) 
# and outputs stall data for the given video seek trial.

# USAGE: python seek_stalls.py youtube_stall_logfile

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
	stall_dict = collections.defaultdict(lambda: 0.0)
	with open(stall_logfilename) as stall_logfile:
		previous_render_call_time = 0.0
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
					stall_dict[previous_frame_presentation_time] = render_call_time - previous_render_call_time
					print("Stall length " + str(render_call_time - previous_render_call_time) + " at frame " + str(previous_frame_presentation_time) + "s before rendering frame " + str(frame_presentation_time) + "s at clock time " + str(previous_render_call_time), file=stall_data_file)
				previous_render_call_time = render_call_time
				previous_frame_presentation_time = frame_presentation_time
	

if __name__ == '__main__':
  main()