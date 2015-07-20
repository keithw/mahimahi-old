#!/usr/bin/python

from __future__ import print_function
import pylab
import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches
import os
import sys
import re
import collections
import pprint
import math

def get_filenames_list(directory_path):
	filenames_list = []
	for dirpath,_,filenames in os.walk(directory_path):
		for f in filenames:
			filenames_list += [os.path.abspath(os.path.join(dirpath, f))]
	return filenames_list

def get_CDF_value(ssim_score, SSIM_scores_data_points_list):
	i = 0
	while(i < len(SSIM_scores_data_points_list)):
		if(float(SSIM_scores_data_points_list[i]) >= float(ssim_score)):
			break
		i += 1
	CDF = float(i)/len(SSIM_scores_data_points_list)
	return CDF

def sc_get_next_resolution(resolution):
	if resolution == "":
		return "1080"
	if resolution == "1080":
		return "720"
	if resolution == "720":
		return "480"
	if resolution == "480":
		return "360"
	if resolution == "360":
		return "240"
	if resolution == "240":
		return "144"
	if resolution == "144":
		return "1080"

def sc_plot_CDF_overlay(SSIM_index, output_filename):
	CDF_data_points_map = {}
	for resolution in SSIM_index:
		SSIM_index[resolution].sort()
		SSIM_scores_data_points_list = SSIM_index[resolution]
		SSIM_scores_x_axis_list = list()
		i = 0.0
		while(i <= 1.0):
			SSIM_scores_x_axis_list += [i]
			i += 0.001
		CDF_data_points_list = list()
		for ssim_score in SSIM_scores_x_axis_list:
			CDF_data_points_list += [get_CDF_value(ssim_score, SSIM_scores_data_points_list)]
		CDF_data_points_map[resolution] = CDF_data_points_list
	fig, ax = plt.subplots()
	axes = [ax, ax.twinx(), ax.twinx(), ax.twinx(), ax.twinx(), ax.twinx()]
	colors = ('Blue','Red', 'Green', 'Orange', 'Purple', 'Cyan')
	resolution = ""
	resolution = sc_get_next_resolution(resolution)
	for a, color in zip(axes, colors):
		a.plot(SSIM_scores_x_axis_list, CDF_data_points_map[resolution], color=color)
		a.set_ylim([-.1, 1.1])
		a.tick_params(axis='y', color=color)	
		resolution = sc_get_next_resolution(resolution)	
	axes[0].set_xlabel('SSIM score')
	ax.set_xlim([0.6, 1.0])
	ax.set_ylabel('CDF')
	blue_patch = mpatches.Patch(color='blue', label='1080')
	red_patch = mpatches.Patch(color='red', label='720')
	green_patch = mpatches.Patch(color='green', label='480')
	orange_patch = mpatches.Patch(color='orange', label='360')
	purple_patch = mpatches.Patch(color='purple', label='240')
	cyan_patch = mpatches.Patch(color='cyan', label='144')
	plt.legend(handles=[blue_patch, red_patch, green_patch, orange_patch, purple_patch, cyan_patch], loc='upper center', bbox_to_anchor=(0.25, 1.05),
          ncol=3, fancybox=True, shadow=True)
	plt.savefig(output_filename)
	os.system('eog ' + output_filename + '&')
	plt.clf()

def sc_read_SSIM_index(index_directory):
	index = collections.defaultdict(lambda: list())
	filenames = get_filenames_list(index_directory)
	for filename in filenames:
		resolution = re.search("[0-9]+x([0-9]+)", filename).group(1)
		with open(filename) as index_file:
			for line in index_file:
				match_object = re.search("[0-9]+ ([0-9]+.[0-9]+) [A-Z] [0-9]+ ([0-9]+)", line)
				if match_object:
					SSIM_score = match_object.group(1)
					index[resolution] += [SSIM_score]
	return index
	
def main():
	SSIM_index = sc_read_SSIM_index(sys.argv[1])
	sc_plot_CDF_overlay(SSIM_index, "./CDF_SSIM_Resolution_Plot.png")




if __name__ == '__main__':
  main()
