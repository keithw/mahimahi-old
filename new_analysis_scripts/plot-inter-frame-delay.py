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
    if len( sys.argv ) is not 2:
        raise ValueError("Usage: python plot-inter-frame-delay.py inter-frame-delay-directory")
    delay_logs_folder = sys.argv[1]

    delays_list = []
    for dirpath,_,filenames in os.walk(delay_logs_folder):
        for f in filenames:
            filepath = os.path.abspath(os.path.join(dirpath, f))
            match_object = re.search("inter-frame-delay.dat", filepath)
            if match_object: # change this to simpler match
                print("parsing " + filepath)
                with open(filepath) as delay_logfile:
                    for line in delay_logfile:
                        delays_list.append(Decimal(line))
    plt.plot(delays_list, color="blue")
    #plt.xlabel('Time in video (seconds)')
    #plt.ylabel('Stall duration (seconds)')
    #plt.ylim([-2, 20])
    #plt.xlim([-30, 920])
    plt.savefig("inter-frame-delay-cdf.pdf")
    plt.clf()

if __name__ == '__main__':
  main()
