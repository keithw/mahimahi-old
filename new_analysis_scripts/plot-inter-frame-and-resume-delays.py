from __future__ import print_function
import os
import sys
import re
import pprint
import math
from decimal import *
import matplotlib
matplotlib.use('pdf') # Must be before importing matplotlib.pyplot or pylab! Default uses x window manager and won't work cleanly in cloud installations.
from matplotlib import collections
import numpy as np
import pylab
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
 
def main():
    if len( sys.argv ) is not 3:
        raise ValueError("Usage: python plot-inter-frame-delay.py inter-frame-delay-directory dataset-title")
    delay_logs_folder = sys.argv[1]
    dataset_title = sys.argv[2]

    inter_frame_delays_list = []
    resume_delays_list = []
    rebuffering_ratios = []
    for dirpath,_,filenames in os.walk(delay_logs_folder):
        for f in filenames:
            filepath = os.path.abspath(os.path.join(dirpath, f))
            match_object = re.search("inter-frame-delays.dat", filepath)
            if match_object: # change this to simpler match
                print("parsing " + filepath)
                with open(filepath) as delay_logfile:
                    total_playback_time = 0.0
                    rebuffering_time = 0.0
                    for line in delay_logfile:
                        inter_frame_delay = float(line)
                        inter_frame_delays_list.append(inter_frame_delay)
                        total_playback_time += inter_frame_delay
                        if inter_frame_delay > .1:
                            rebuffering_time += inter_frame_delay
                rebuffering_ratios.append(rebuffering_time / total_playback_time)

            match_object = re.search("resume-delays.dat", filepath)
            if match_object:
                print("parsing " + filepath)
                with open(filepath) as resume_delay_logfile:
                    for line in resume_delay_logfile:
                        resume_delays_list.append(float(line))

    sorted_vals = np.sort( inter_frame_delays_list )
    yvals = 1-(np.arange(len(sorted_vals))/float(len(sorted_vals)))
    plt.plot( sorted_vals, yvals )

    plt.title("CCDF of all inter-frame delays for " + dataset_title +" ("+ str(len(sorted_vals))+" datapoints)")
    plt.xscale('log')
    plt.xlabel('Inter-frame delay (seconds)')
    plt.yscale('log')
    filename = dataset_title + "-inter-frame-delays-ccdf.pdf"
    print("Writing " + filename +"..")
    plt.savefig(filename)
    plt.clf()

    sorted_vals = np.sort( resume_delays_list )
    yvals = np.arange(len(sorted_vals))/float(len(sorted_vals))
    plt.plot( sorted_vals, yvals )
    plt.title("CDF of seek delays for " + dataset_title +" ("+ str(len(sorted_vals))+" datapoints)")
    plt.xlabel('Resume duration (seconds)')
    filename = dataset_title + "-resume-delays-cdf.pdf"
    print("Writing " + filename +"..")
    plt.savefig(filename)
    plt.clf()

    sorted_vals = np.sort( rebuffering_ratios )
    #TODO FIX yvals for all CDFs so it always ends with 1
    yvals = np.arange(len(sorted_vals))/float(len(sorted_vals))
    plt.plot( sorted_vals, yvals )
    plt.title("CDF rebuffering ratios for " + dataset_title +" ("+ str(len(sorted_vals))+" runs)")
    plt.xlabel('Rebuffering ratio')
    filename = dataset_title + "-rebuffering-ratios-cdf.pdf"
    print("Writing " + filename +"..")
    plt.savefig(filename)
    plt.clf()

if __name__ == '__main__':
  main()
