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
 
def get_cdf( unsorted_vals ):
    xvals = np.sort( unsorted_vals )
    yvals = (np.arange(len(xvals)) + 1)/float(len(xvals)) # range from 1 / len(xvals) to 1 inclusive
    return (xvals, yvals)

def main():
    if len( sys.argv ) is not 2:
        raise ValueError("Usage: python plot-inter-frame-delay.py inter-frame-delay-directory")
    delay_logs_folder = sys.argv[1]
    _, dataset_title  = os.path.split(os.path.abspath(delay_logs_folder))

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

    (xvals, yvals) = get_cdf( inter_frame_delays_list )
    plt.plot( xvals, 1-yvals )

    plt.title("CCDF of all inter-frame delays for " + dataset_title +" ("+ str(len(xvals))+" datapoints)")
    plt.xscale('log')
    plt.xlabel('Inter-frame delay (seconds)')
    plt.yscale('log')
    filename = dataset_title + "-inter-frame-delays-ccdf.pdf"
    print("Writing " + filename +"..")
    plt.savefig(filename)
    plt.clf()

    (xvals, yvals) = get_cdf( resume_delays_list )
    plt.plot( xvals, yvals )
    plt.title("CDF of seek delays for " + dataset_title +" ("+ str(len(xvals))+" datapoints)")
    plt.xlabel('Resume duration (seconds)')
    filename = dataset_title + "-resume-delays-cdf.pdf"
    print("Writing " + filename +"..")
    plt.savefig(filename)
    plt.clf()

    (xvals, yvals) = get_cdf( rebuffering_ratios )
    plt.plot( xvals, yvals )
    plt.title("CDF rebuffering ratios for " + dataset_title +" ("+ str(len(xvals))+" runs)")
    plt.xlabel('Rebuffering ratio')
    filename = dataset_title + "-rebuffering-ratios-cdf.pdf"
    print("Writing " + filename +"..")
    plt.savefig(filename)
    plt.clf()

if __name__ == '__main__':
  main()
