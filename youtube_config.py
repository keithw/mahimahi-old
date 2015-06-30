#!/usr/bin/python

# This script runs mm-webrecord to save requests response pairs from Youtube. 
# If saved request response pairs already exit, the user can elect to skip 
# running mm-webrecord again. Next the script runs youtube-dl on all the 
# necessary media files from YouTube. Again if these media files already
# exit the user can elect to skip this step. 

# The media files are stored in a ./media_files directory and
# the mm-webrecord files are stored in a ./saved_requests directory. 
# These two directories are automatically created by the script.

# USAGE: python youtube_config.py youtube_url

import sys
import re
import os

def get_yes_or_no(message): 
	while(True):
		response = raw_input(message)
		if(response == "y" or response == "Y"):
			return True
		if(response == "n" or response == "N"):
			return False
		print "please response with y or n "

def main():
	if not os.path.exists("./saved_requests"):
		os.makedirs("./saved_requests")
	if not os.path.exists("./media_files"):
		os.makedirs("./media_files")
	if not os.path.exists("./youtube_logs"):
		os.makedirs("./youtube_logs")
	youtube_url = sys.argv[1]
	match_object = re.search("/embed/([_a-zA-Z0-9\-]+)", youtube_url)
	video_id = ""
	if not match_object:
  		print "ERROR: " + youtube_url + " is not a valid embed youtube url" 
  		sys.exit()
  	else:
  		video_id = match_object.group(1)
  		print "Detected youtube url with video id " + video_id
	media_files_path =  os.path.dirname(os.path.realpath(__file__)) + "/media_files/" + video_id
	saved_requests_path = os.path.dirname(os.path.realpath(__file__)) + "/saved_requests/" + video_id
	print media_files_path
	print saved_requests_path
	print "Checking for saved session data......"
	print
	if os.path.exists(saved_requests_path): 
		should_run_mm_webrecord = get_yes_or_no("It appears as if you have already recorded session data YouTube url. Would you like to overwrite your previous recording? y/n  \n")
		if(should_run_mm_webrecord):
			print "RUNNING mm-webrecord to record new session. Please play video when browser pops up and wait 20 seconds to save enough requests."
			os.system("rm -rf " + saved_requests_path)
			os.system("mm-webrecord " + saved_requests_path + " chromium-browser --ignore-certificate-errors --user-data-dir=/tmp/nonexistent$(date +%s%N) " + youtube_url)
		else: 
			print "SKIPPING mm-webrecord......"
	else:
		print "RUNNING mm-webrecord to record new session. Please play video when browser pops up and wait 20 seconds to save enough requests."
		os.system("rm -rf " + saved_requests_path)
		os.system("mm-webrecord " + saved_requests_path + " chromium-browser --ignore-certificate-errors --user-data-dir=/tmp/nonexistent$(date +%s%N) " + youtube_url)
	print
	print "Checking for downloaded media files......"
	print
	if os.path.exists(media_files_path):
		should_run_youtube_dl = get_yes_or_no("It appears you have already downloaded this youtube video locally. Would you like to overwrite your previous download and re-download this video? y/n  \n")
		if(should_run_youtube_dl):
			print "RUNNING youtube-dl on all DASH audio and video files for " + youtube_url
			os.system("rm -rf " + media_files_path)
			os.system("python youtube_download.py " + youtube_url)
		else: 
			print "SKIPPING youtube_download......"
	else:
		print "RUNNING youtube-dl on all DASH audio and video files for " + youtube_url
		os.system("rm -rf " + media_files_path)
		os.system("python youtube_download.py " + youtube_url)
	print
	print "SUCCESS you are now ready to run python youtube_replay.py " + youtube_url
		

if __name__ == '__main__':
  main()