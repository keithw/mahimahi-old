#!/usr/bin/python

# This script runs mm-webrecord to save requests response pairs from Youtube. 
# If saved request response pairs already exit, the user can elect to skip 
# running mm-webrecord again. Next the script runs youtube-dl on all the 
# necessary media files from YouTube. Again if these media files already
# exit the user can elect to skip this step. 

# The media files are stored in a ./media_files directory and
# the mm-webrecord files are stored in a ./saved_requests directory. 
# These two directories are automatically created by the script.

# USAGE: python youtube_config.py --url='<insert YouTube embed url here>'

# Other options are (the values provided are just for example):

# --video-id='5PoPaxDsA8I'
# --browser-command='../Chromium_Fork/src/out/Release/chrome --enable-logging=stderr --v=1'
# --url='https://www.youtube.com/embed/5PoPaxDsA8I?autoplay=1'


import sys
import re
import os
import subprocess
import collections

def get_yes_or_no(message): 
	while(True):
		response = raw_input(message)
		if(response == "y" or response == "Y"):
			return True
		if(response == "n" or response == "N"):
			return False
		print "please response with y or n "

def main():
	command_line_arguments = collections.defaultdict()
	video_id_re = "--video-id=(.+)"
	browser_command_re = "--browser-command=(.+)"
	url_re = "--url=(.+)"
	for arg in sys.argv:
		video_id_match_object = re.search(video_id_re, arg)
		browser_command_match_object = re.search(browser_command_re, arg)
		url_match_object = re.search(url_re, arg)
		if video_id_match_object:
			command_line_arguments["--video-id"] = video_id_match_object.group(1)
		if browser_command_match_object:
			command_line_arguments["--browser-command"] = browser_command_match_object.group(1)
		if url_match_object:
			command_line_arguments["--url"] = url_match_object.group(1)
	#Configure default parameter values
	video_id = ""
	browser_command = "chromium-browser"
	url = ""
	#Set command line parameters if given
	if "--video-id" in command_line_arguments:
		video_id = command_line_arguments["--video-id"]
	if "--browser-command" in command_line_arguments:
		browser_command = command_line_arguments["--browser-command"]
	if "--url" in command_line_arguments:
		url = command_line_arguments["--url"]		
	if url == "":
		print "ERROR: No url provided. Please pass a valid YouTube url using --url='<insert url here>'."
		sys.exit(1)
	#Set the video id by parsing the embed YouTube url
	if video_id == "":
		match_object = re.search("/embed/([_a-zA-Z0-9\-]+)", url)
		if not match_object:
  			print "ERROR: " + url + " is not a valid embed YouTube url. We cannot parse the video id from the url if it is not valid." 
  			print "ERROR: Without a video id we cannot configure your video. Either use a correctly formatted YouTube embed url or provide a video id for your custom url."
  			print "You can provide a video id with the option --video-id='<insert video id here>' or a url using --url='<insert url here>'."
  			sys.exit(1)
		else:
	  		video_id = match_object.group(1)
	print "Detected YouTube url with video id " + video_id
	#Configure file structure
	if not os.path.exists("./saved_requests"):
		os.makedirs("./saved_requests")
	if not os.path.exists("./media_files"):
		os.makedirs("./media_files")
	if not os.path.exists("./youtube_logs"):
		os.makedirs("./youtube_logs")
	media_files_path =  os.path.dirname(os.path.realpath(__file__)) + "/media_files/" + video_id
	saved_requests_path = os.path.dirname(os.path.realpath(__file__)) + "/saved_requests/" + video_id
	print
	print "The YouTube url is " + url
	print "Downloaded media files will be saved in " + media_files_path
	print "Recorded session data will be saved in " + saved_requests_path
	print "Checking for saved session data......"
	print
	mm_webrecord_command = "mm-webrecord " + saved_requests_path + " " + browser_command + " --start-maximized --ignore-certificate-errors --user-data-dir=/tmp/nonexistent$(date +%s%N) '" + url + "'"
	if os.path.exists(saved_requests_path): 
		should_run_mm_webrecord = get_yes_or_no("It appears as if you have already recorded session data for this video. Would you like to overwrite your previous recording? y/n  \n")
	else:
		should_run_mm_webrecord = True
	if(should_run_mm_webrecord):
		print "RUNNING mm-webrecord to record new session. Please play video when browser pops up and wait 20 seconds to save enough requests.\n"
		os.system("rm -rf " + saved_requests_path)
		if os.system(mm_webrecord_command):
			print "mm-webrecord seems to have failed. Error messages have been posted above. Please fix the errors and run the config script again."
			sys.exit(1)
	else: 
		print "SKIPPING mm-webrecord......"
	print
	print "Checking for downloaded media files......"
	print
	if os.path.exists(media_files_path):
		should_run_youtube_dl = get_yes_or_no("It appears you have already downloaded this youtube video locally. Would you like to overwrite your previous download and re-download this video? y/n  \n")
	else:
		should_run_youtube_dl = True
	if(should_run_youtube_dl):
		print "RUNNING youtube-dl on all DASH audio and video files for " + url
		os.system("rm -rf " + media_files_path)
		if os.system("python youtube_download.py '" + url + "'"):
			sys.exit(1)
	else: 
		print "SKIPPING youtube_download......"
	print
	print "SUCCESS you are now ready to run python youtube_replay.py --url='" + url + "'"
		

if __name__ == '__main__':
  main()