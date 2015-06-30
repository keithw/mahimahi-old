#!/usr/bin/python

# This script downloads video from youtube for the youtube emulation server

# It is meant to be run by youtube_config.py, not by the user. 

# USAGE: python youtube_download.py youtube_url

import sys
import subprocess
import re
import os
import shutil

def delete_filesys_subtree(root_directory):
	for the_file in os.listdir(root_directory):
	    file_path = os.path.join(root_directory, the_file)
	    try:
	        if os.path.isfile(file_path):
	            os.unlink(file_path)
	        elif os.path.isdir(file_path): shutil.rmtree(file_path)
	    except Exception, e:
	        print e

def get_media_resolution(line):
	match_object = re.search("DASH video", line)
	if(match_object):
		match_object = re.search("([0-9]+x[0-9]+)", line)
		if(match_object):
			return match_object.group(1)
	match_object = re.search("DASH audio", line)
	if(match_object):
		match_object = re.search("DASH audio\t[0-9]+k , (?:m4a_dash container, )?(.+)", line)
		if(match_object):
			return match_object.group(1)
	return ""

def main():
	print
	youtube_url = sys.argv[1]
  	match_object = re.search("/embed/([_a-zA-Z0-9\-]+)", youtube_url)
  	video_id = ""
	if not match_object:
		print "ERROR: " + youtube_url + " is not a valid embed youtube url" 
		sys.exit()
  	else:
  		video_id = match_object.group(1)
  		print "Running youtube-dl on video id " + video_id + "......"
  		print
  		print "Available formats are as follows: "
  		formats_command = "youtube-dl -F " + youtube_url
  		print "Runnding command " + formats_command + "......"
  		proc = subprocess.Popen(formats_command, stdout=subprocess.PIPE, shell=True)
  		(out, err) = proc.communicate()
  		print out
  		print "Grabbing all mp4, webm, and m4a DASH files for video id " + video_id + "......"
  		print
  		newpath =  os.path.dirname(os.path.realpath(__file__)) + "/media_files/" + video_id
		print "Storing media files in " + newpath + "......"
		print
		if os.path.exists(newpath): 
			delete_filesys_subtree(newpath)
			os.makedirs(newpath + "/audio")
			os.makedirs(newpath + "/video")
			os.makedirs(newpath + "/audio/mp4")
			os.makedirs(newpath + "/video/mp4")
			os.makedirs(newpath + "/video/webm")
			os.makedirs(newpath + "/audio/webm")
		for lno, line in enumerate(out.splitlines()):
			if(re.search("DASH video", line) or re.search("DASH audio", line)):
				print "Downloading file specified by " + line
				download_id_match_object = re.match("([0-9]+)", line)
				if not download_id_match_object: 
					print
					print "ERROR: Line " + line + " has no download identifier."
				else: 
					download_id = download_id_match_object.group(1)
					mime_prefix = ""
					mime_suffix = ""
					video_resolution = ""
					if(re.search("audio", line)):
						mime_prefix = "audio"
					if(re.search("video", line)):
						mime_prefix = "video"
						video_resolution_match_object = re.search("([0-9]+p)", line)
						if(video_resolution_match_object):
							video_resolution = video_resolution_match_object.group(1)
					if(re.search("webm", line)):
						mime_suffix = "webm"
					if(re.search("mp4", line)):
						mime_suffix = "mp4"
					if(re.search("m4a", line)):
						mime_suffix = "mp4"
					if(mime_prefix == "" or mime_suffix == ""):
						print
						print "ERROR: Could not parse line " + line + " for mime format."
						sys.exit()
					mime_format = mime_prefix + "/" + mime_suffix
					destination_filename = newpath + "/" + mime_format + "/" + download_id
					download_command = "youtube-dl -o " + destination_filename + " -f " + download_id + " " + youtube_url
					print "Runnding command " + download_command + "......"
					proc = subprocess.Popen(download_command, stdout=subprocess.PIPE, shell=True)
					(out, err) = proc.communicate()
					print out
					filename_suffix = get_media_resolution(line); 
					if(filename_suffix == ""):
						filename_suffix = download_id
					new_filename = newpath + "/" + mime_format + "/" + filename_suffix
					os.rename(destination_filename, new_filename)

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()