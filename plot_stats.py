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

def get_filenames_list(directory_path):
	filenames_list = []
	for dirpath,_,filenames in os.walk(directory_path):
		for f in filenames:
			filenames_list += [os.path.abspath(os.path.join(dirpath, f))]
	return filenames_list

def main():
	filenames_list = get_filenames_list("./youtube_analysis_output/")
	stats_filename_list = list()
	std_dev_list = list()
	mean_list = list()
	for filename in filenames_list:
		filename_match_object = re.search("stats.txt", filename)
		if filename_match_object:
			with open(filename) as stats_file:
				mean = 0.0
				std_dev = 0.0
				for line in stats_file:
					mean_match_object = re.search("Mean SSIM score: (.+)", line)
					std_dev_match_object = re.search("Standard Deviation of SSIM scores: (.+)", line)
					if mean_match_object:
						mean = mean_match_object.group(1)
					if std_dev_match_object:
						std_dev = std_dev_match_object.group(1)
				mean_list += [mean]
				std_dev_list += [std_dev]
				trial_name_match_object = re.search(".+(Verizon_Driving_.+)/stats.txt", filename)
				stats_filename_list += [trial_name_match_object.group(1)]
	filename_id_list = list()
	for filename in stats_filename_list:
		match_object = re.search("No_Log", filename)
		if match_object:
			filename_id_list += [3]
			continue
		match_object = re.search("Chromium", filename)
		if match_object:
			filename_id_list += [2]
			continue
		match_object = re.search("Chrome", filename)
		if match_object:
			filename_id_list += [0]
			continue
		else: 
			filename_id_list += [1]
			continue
	plt.plot(filename_id_list, mean_list, 'bo')
	plt.xlabel('Trial ID')
	plt.ylabel('Mean SSIM Score')
	plt.ylim([0, 1.5])
	plt.xlim([-1, 5])
	plt.savefig("./mean_SSIM_all_trials.png")
	os.system('eog ./mean_SSIM_all_trials.png&')
	plt.clf()
	plt.plot(filename_id_list, std_dev_list, 'bo')
	plt.xlabel('Trial ID')
	plt.ylabel('Standard Deviation SSIM Score')
	plt.ylim([0, 0.15])
	plt.xlim([-1, 5])
	plt.savefig("./std_dev_SSIM_all_trials.png")
	os.system('eog ./std_dev_SSIM_all_trials.png&')
	plt.clf()


if __name__ == '__main__':
  main()