#!/usr/bin/python

#Usage: python get_SSIM_index.py 'youtube_url'

import sys
import subprocess
import os
import re

def get_filenames_list(directory_path):
	filenames_list = []
	for dirpath,_,filenames in os.walk(directory_path):
		for f in filenames:
			filenames_list += [os.path.abspath(os.path.join(dirpath, f))]
	return filenames_list

def main():
	youtube_url = sys.argv[1]
  	match_object = re.search("/embed/([_a-zA-Z0-9\-]+)", youtube_url)
  	video_id = ""
	if not match_object:
		print "ERROR: " + youtube_url + " is not a valid embed youtube url" 
		sys.exit()
  	else:
  		video_id = match_object.group(1)
		if not os.path.exists("./SSIM_indexes"):
			os.system("mkdir SSIM_indexes")
		if not os.path.exists("./SSIM_indexes/" + video_id):
			os.system("mkdir ./SSIM_indexes/" + video_id)
		process_list = list()
		for filename in get_filenames_list("./media_files/" + video_id + "/video/"):
			filename_extension = re.search("([0-9]+x[0-9]+)", filename).group(1)
			output_filename = "./SSIM_indexes/" + video_id + "/" + filename_extension
			process_list += [subprocess.Popen("../SSIM/src/ssim ../charade.mkv " + filename + " > " + output_filename, shell=True)]
		for process in process_list:
			process.wait()
		

if __name__ == '__main__':
  main()