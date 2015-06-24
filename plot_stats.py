#!/usr/bin/python

# This script replicates the instrumentation error bars graph for 
# mean SSIM and standard deviation across browsers for a given video trial.

# USAGE: python plot_stats.py 

from __future__ import print_function
import sys
import re
from decimal import *
import pylab
import matplotlib.pyplot as plt 
import collections
import os
import matplotlib.patches as mpatches

def get_filenames_list(directory_path):
	filenames_list = []
	for dirpath,_,filenames in os.walk(directory_path):
		for f in filenames:
			filenames_list += [os.path.abspath(os.path.join(dirpath, f))]
	return filenames_list

def main():
	filenames_list = get_filenames_list("./youtube_analysis_output/")
	stats_list = list()
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
				trial_name_match_object = re.search(".+(Verizon_Driving_.+)/stats.txt", filename)
				if trial_name_match_object:
					stats_list += [(trial_name_match_object.group(1), mean, std_dev)]
	stats_list.sort(key=lambda tup: tup[0])
	filename_id_list = list()
	for filename_tup in stats_list:
		filename = filename_tup[0]
		match_object = re.search("No_Log", filename)
		if match_object:
			filename_id_list += ["Chromium From Source"]
			continue
		match_object = re.search("Chromium", filename)
		if match_object:
			filename_id_list += ["Chromium From Source - Instrumented"]
			continue
		match_object = re.search("Chrome", filename)
		if match_object:
			filename_id_list += ["Google Chrome"]
			continue
		else: 
			filename_id_list += ["Chromium Ubuntu Distribution"]
			continue
	for index,filename_id in enumerate(filename_id_list):
		color="black"
		if filename_id == "Chromium From Source":
			color="blue"
		if filename_id == "Chromium From Source - Instrumented":
			color="red"
		if filename_id == "Google Chrome":
			color="green"
		if filename_id == "Chromium Ubuntu Distribution":
			color="orange"
		mean = float(stats_list[index][1])
		std_dev = float(stats_list[index][2])
		plt.errorbar(index, mean, yerr=std_dev, color=color)
	blue_patch = mpatches.Patch(color='blue', label='Chromium From Source')
	red_patch = mpatches.Patch(color='red', label='Chromium From Source - Instrumented')
	green_patch = mpatches.Patch(color='green', label='Google Chrome')
	orange_patch = mpatches.Patch(color='orange', label='Chromium Ubuntu Distribution')
	plt.legend(handles=[blue_patch, red_patch, green_patch, orange_patch], bbox_to_anchor=(0.77, 1.05), fancybox=True, shadow=True)
	plt.xlabel('Trial Number')
	plt.ylabel('Mean SSIM Score')
	plt.ylim([0.85, 1.00])
	plt.xlim([-.5, 14])
	plt.savefig("./SSIM_all_trials.png")
	os.system('eog ./SSIM_all_trials.png&')
	plt.clf()


if __name__ == '__main__':
  main()

