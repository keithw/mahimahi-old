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
getcontext().prec = 6 # the precision of our get time syscall

# map takes only one argument so use a three-tuple as input
def get_inter_frame_delay((stall_logfilename, trial_id, output_directory)):
    inter_frame_delay_filename = output_directory + "/" + trial_id + "/" + "inter-frame-delays.dat"
    resumes_delay_filename = output_directory + "/" + trial_id + "/" + "resume-delays.dat"
    with open(inter_frame_delay_filename, 'w') as inter_frame_delay_file, open(resumes_delay_filename, 'w') as resumes_delay_file, open(stall_logfilename) as stall_logfile:

        first_render_time_of_last_frame = Decimal(0.0)
        time_in_video_of_last_frame = float(0)

        for line in stall_logfile:
            match_object = re.search("RENDER CALL ON: ([0-9]+(?:\.[0-9]+)?)s TIME: (.+)", line)
            if match_object:
                if first_render_time_of_last_frame == 0: # very first render call
                    first_render_time_of_last_frame = Decimal(match_object.group(2))
                    time_in_video_of_last_frame = float(match_object.group(1))
                else: # every other render call
                    system_time_of_render_call = Decimal(match_object.group(2))
                    time_in_video_of_frame_rendered = float(match_object.group(1))

                    if time_in_video_of_frame_rendered != time_in_video_of_last_frame: # We are rendering a new frame
                        inter_frame_delay_time = system_time_of_render_call - first_render_time_of_last_frame - (Decimal(1) / Decimal(60))
                        print(inter_frame_delay_time, file=inter_frame_delay_file)

                        if (time_in_video_of_frame_rendered - time_in_video_of_last_frame) > 1: # assume seek if video jumps >1 s
                            print(inter_frame_delay_time, file=resumes_delay_file)

                        first_render_time_of_last_frame = system_time_of_render_call
                        time_in_video_of_last_frame = time_in_video_of_frame_rendered


        print("Finished parsing " + trial_id)
 
def main():
    if len( sys.argv ) is not 3:
        raise ValueError("Usage: python parse-inter-frame-delay.py youtube_logs_folder output_directory")
    logs_folder = sys.argv[1]
    output_directory = sys.argv[2]
    if os.path.exists(output_directory):
        os.system("rm -rf " + output_directory)
    os.system("mkdir " + output_directory)

    args_list = []
    for dirpath,_,filenames in os.walk(logs_folder):
        for f in filenames:
            filepath = os.path.abspath(os.path.join(dirpath, f))
            match_object = re.search("stall-log-(.+).txt", filepath)
            if match_object:
                trial_id = match_object.group(1)
                # TODO maybe don't delete existing directory here
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
