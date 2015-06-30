#!/usr/bin/python

# This script checks for mm-webrecord saved request/response pairs and
# also checks for media files in the directory for the youtube link. 

# The media files must be stored in a media_files directory and
# the mm-webrecord files must be stored in a saved_requests directory. 
# Note that these two directories are automatically created by 
# youtube_config.py. 

# USAGE: python youtube_replay.py youtube_url

import sys
import os
import re

def main():
	youtube_url = sys.argv[1]
	match_object = re.search("/embed/([_a-zA-Z0-9\-]+)", youtube_url)
	video_id = ""
	if not match_object:
  		print "ERROR: " + youtube_url + " is not a valid embed youtube url" 
  		sys.exit()
  	else:
  		video_id = match_object.group(1)
  		print
  		print "Running mm-youtubereplay on video id " + video_id + "......"
  		print 
	media_files_path =  os.path.dirname(os.path.realpath(__file__)) + "/media_files/" + video_id
	saved_requests_path = os.path.dirname(os.path.realpath(__file__)) + "/saved_requests/" + video_id
	if not os.path.exists(saved_requests_path): 
		print "ERROR: It appears there is no saved session data for the youtube video corresponding to video id " + video_id
		print "ERROR: Recorded session data could not be found where it is expected in " + saved_requests_path
		print "ERROR: Please run python youtube_config.py " + youtube_url + " to correct this error "
		print
		sys.exit()
	if not os.path.exists(media_files_path):
		print "ERROR: It appears there are no saved media files for the youtube video corresponding to video id " + video_id
		print "ERROR: Downloaded media files could not be found where they are expected in " + media_files_path
		print "ERROR: Please run python youtube_config.py " + youtube_url + " to correct this error "
		print
		sys.exit()
	os.system("mm-youtubereplay " + saved_requests_path + " chromium-browser --ignore-certificate-errors --user-data-dir=/tmp/nonexistent$(date +%s%N) " + youtube_url)
		

if __name__ == '__main__':
  main()
