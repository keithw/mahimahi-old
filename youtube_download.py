#!/usr/bin/python

# This script downloads video from youtube for the youtube emulation server

# It is meant to be run by youtube_record.py, not by the user. 

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

def main():
  match_object = re.search("\?v=(.+)", sys.argv[1])
  if not match_object:
  	print sys.argv[1] + " is not a valid youtube url" 
  else:
  	video_id = match_object.group(1)
  	print video_id 
  	proc = subprocess.Popen("youtube-dl -F " + sys.argv[1], stdout=subprocess.PIPE, shell=True)
  	(out, err) = proc.communicate()
  	print out
  	print 'Grabbing all available DASH video and DASH audio files for ', sys.argv[1]
  	newpath =  os.path.dirname(os.path.realpath(__file__)) + "/media_files/" + video_id
	print "Storing media files in " + newpath
	if os.path.exists(newpath): 
		delete_filesys_subtree(newpath)
		os.makedirs(newpath)
		os.makedirs(newpath + "/audio")
		os.makedirs(newpath + "/video")
		os.makedire(newpath + "/audio/mp4")
		os.makedire(newpath + "/video/mp4")
		os.makedire(newpath + "/video/webm")
		os.makedire(newpath + "/audio/webm")
	file_id = 1
	for lno, line in enumerate(out.splitlines()):
		if(re.search("DASH", line)):
			print "LINE " + str(lno) + " " + line
			download_id_match_object = re.match("([0-9]+)", line)
			if not download_id_match_object: 
				print "ERROR: Line " + line + " has no download identifier."
				sys.exit()
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
					print "ERROR: Could not parse line " + line + " for mime format."
					sys.exit()
				mime_format = mime_prefix + "/" + mime_suffix
				proc = subprocess.Popen("youtube-dl -o " + newpath + "/" + mime_format + " -f " + download_id + " " + sys.argv[1], stdout=subprocess.PIPE, shell=True)
				(out, err) = proc.communicate()
				destination_filename = ""
				for line in out.splitlines():
					destination_filename_match_object = re.search("Destination: (.+)", line)
					if(destination_filename_match_object): 
						destination_filename = destination_filename_match_object.group(1)
				if(destination_filename == ""):
					print "ERROR: Could not parse destination filename."
					sys.exit()
				filename_suffix = ""
				if(video_resolution == ""):
					filename_suffix = mime_prefix + file_id
					file_id = file_id + 1
				else: 
					filename_suffix = video_resolution
				new_filename = newpath + "/" + mime_format + "/" + filename_suffix
				os.rename(destination_filename, new_filename)

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()