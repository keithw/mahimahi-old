#!/usr/bin/python

# This script reads the log file from mm-youtubereplay (youtube_replay.py)
# and outputs stall data for the given video trial.

# Usage: python plot_stall_logfile.py youtube_stall_logfile

from __future__ import print_function
import sys
import re
from decimal import *
import matplotlib
matplotlib.use('pdf') # Must be before importing matplotlib.pyplot or pylab! Default uses x window manager and won't work cleanly in cloud installations.
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
    stall_length_list = list()
    stall_presentation_time = list()
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
                    stall_length_list += [render_call_time - previous_render_call_time]
                    stall_presentation_time += [Decimal(frame_presentation_time)]
                else:
                    stall_length_list += [0]
                    stall_presentation_time += [Decimal(frame_presentation_time)]
                previous_render_call_time = render_call_time
                previous_frame_presentation_time = frame_presentation_time
    previous_time = 0
    previous_time_so_far = list()
    length_list_so_far = list()
    for i, time in enumerate(stall_presentation_time):
        if time - previous_time > 30:
            plt.plot(previous_time_so_far, length_list_so_far, color="blue")
            previous_time_so_far = list()
            length_list_so_far = list()
        previous_time_so_far += [time]
        length_list_so_far += [stall_length_list[i]]
        previous_time = time
    plt.plot(previous_time_so_far, length_list_so_far, color="blue")
    plt.xlabel('Time in video (seconds)')
    plt.ylabel('Stall duration (seconds)')
    plt.ylim([-2, 20])
    plt.xlim([-30, 920])
    plt.savefig("./stalls.pdf")
    plt.clf()

if __name__ == '__main__':
  main()
