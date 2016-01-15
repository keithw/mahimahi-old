from __future__ import print_function
import os
import sys
import multiprocessing
from multiprocessing import Pool
import re
import collections
import pprint
import math
from decimal import *

# map takes only one argument so use a three-tuple as input
def get_inter_frame_delay((stall_logfilename, trial_id, output_directory)):
    with open(output_directory + "/" + trial_id + "/" + "inter-frame-delay.dat", 'w') as output_data_file:
        with open(stall_logfilename) as stall_logfile:
            previous_render_call_time = Decimal(0.0)
            for line in stall_logfile:
                match_object = re.search("RENDER CALL ON: ([0-9]+(?:\.[0-9]+)?)s TIME: (.+)", line)
                if match_object:
                    render_call_time = Decimal(match_object.group(2))
                    #frame_presentation_time = match_object.group(1)
                    if previous_render_call_time != 0:
                        print(render_call_time - previous_render_call_time, file=output_data_file)

                    previous_render_call_time = render_call_time
            print("Finished parsing " + trial_id)
 
def main():
    if len( sys.argv ) is not 3:
        raise ValueError("Usage: python parse-inter-frame-delay.py youtube_logs_folder output_directory")
    logs_folder = sys.argv[1]
    output_directory = sys.argv[2]
    if not os.path.exists(output_directory):
        os.system("mkdir " + output_directory)

    args_list = []
    for dirpath,_,filenames in os.walk(logs_folder):
        for f in filenames:
            filepath = os.path.abspath(os.path.join(dirpath, f))
            match_object = re.search("stall-log-(.+).txt", filepath)
            if match_object:
                trial_id = match_object.group(1)
                # TODO maybe don't delete existing directory here
                if os.path.exists(output_directory + "/" + trial_id):
                    os.system("rm -rf " + output_directory + "/" + trial_id)
                os.system("mkdir " + output_directory + "/" + trial_id)
                args_list.append((filepath, trial_id, output_directory))

    if len(args_list) is 0:
        print("No stall-log files found in " + logs_folder)
    else:
        print("Processing " + str(len(args_list)) + " stall log files...")

    # Use process pool to parallelize calling get_inter_frame_delay
    Pool(processes=multiprocessing.cpu_count()).map(get_inter_frame_delay, args_list)

if __name__ == '__main__':
  main()
