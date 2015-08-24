#!/usr/bin/python

# This script checks for mm-webrecord saved request/response pairs and
# also checks for media files in the directory for the youtube link. 

# The media files must be stored in a media_files directory and
# the mm-webrecord files must be stored in a saved_requests directory. 
# Note that these two directories are automatically created by 
# youtube_config.py. 

# USAGE: python youtube_replay.py --url='<insert YouTube embed url here>' --mahimahi-options='<insert optional mahimahi options here>'

# Other options are (the values provided are just for example):

# --video-id='5PoPaxDsA8I'
# --browser-command='../Chromium_Fork/src/out/Release/chrome --enable-logging=stderr --v=1'
# --mahimahi-options='mm-delay 20 mm-link ./traces/Verizon-LTE-driving.up ./traces/Verizon-LTE-driving.down --'
# --url='https://www.youtube.com/embed/5PoPaxDsA8I?autoplay=1'


import sys
import os
import re
import collections

def main():
	command_line_arguments = collections.defaultdict()
	video_id_re = "--video-id=(.+)"
	browser_command_re = "--browser-command=(.+)"
	mahimahi_options_re = "--mahimahi-options=(.+)"
	url_re = "--url=(.+)"
	env_string_re = "--env=(.+)"
	for arg in sys.argv:
		video_id_match_object = re.search(video_id_re, arg)
		browser_command_match_object = re.search(browser_command_re, arg)
		mahimahi_options_match_object = re.search(mahimahi_options_re, arg)
		url_match_object = re.search(url_re, arg)
		env_match_object = re.search(env_string_re, arg)
		if video_id_match_object:
			command_line_arguments["--video-id"] = video_id_match_object.group(1)
		if browser_command_match_object:
			command_line_arguments["--browser-command"] = browser_command_match_object.group(1)
		if mahimahi_options_match_object:
			command_line_arguments["--mahimahi-options"] = mahimahi_options_match_object.group(1)
		if url_match_object:
			command_line_arguments["--url"] = url_match_object.group(1)
		if env_match_object:
			command_line_arguments["--env"] = env_match_object.group(1)
	#Configure default parameter values
	video_id = ""
	browser_command = "chromium-browser"
	mahimahi_options = ""
	url = ""
	env_string = ""
	#Set command line parameters if given
	if "--video-id" in command_line_arguments:
		video_id = command_line_arguments["--video-id"]
	if "--browser-command" in command_line_arguments:
		browser_command = command_line_arguments["--browser-command"]
	if "--mahimahi-options" in command_line_arguments:
		mahimahi_options = command_line_arguments["--mahimahi-options"]
	if "--url" in command_line_arguments:
		url = command_line_arguments["--url"]
	if "--env" in command_line_arguments:
		env_string = command_line_arguments["--env"]
	if url == "":
		print "ERROR: No url provided. Please pass a valid YouTube url using --url='<insert url here>'."
		sys.exit(1)
	print(env_string)
	env_array = env_string.split(" ")
	env_var_re = "([A-Z_]+)=(.+)"
	for env_var in env_array:
		env_var_match_object = re.search(env_var_re, env_var)
		if not env_var_match_object:
			print "ERROR: Incorrectly formatted environment variable " + env_var + " in command line arguments."
			sys.exit(1)
		else:
			os.environ[env_var_match_object.group(1)] = env_var_match_object.group(2)
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
	print
	print "Running mm-youtubereplay on video id " + video_id + "......"
	print 
	os.system("rm ./youtube_logs/" + video_id + ".txt")
	media_files_path =  os.path.dirname(os.path.realpath(__file__)) + "/media_files/" + video_id
	saved_requests_path = os.path.dirname(os.path.realpath(__file__)) + "/saved_requests/" + video_id
	if not os.path.exists(saved_requests_path): 
		print "ERROR: It appears there is no saved session data for the youtube video corresponding to video id " + video_id
		print "ERROR: Recorded session data could not be found where it is expected in " + saved_requests_path
		print "ERROR: Please run python youtube_config.py " + url + " to correct this error "
		print
		sys.exit(1)
	if not os.path.exists(media_files_path):
		print "ERROR: It appears there are no saved media files for the youtube video corresponding to video id " + video_id
		print "ERROR: Downloaded media files could not be found where they are expected in " + media_files_path
		print "ERROR: Please run python youtube_config.py " + url + " to correct this error "
		print
		sys.exit(1)
	youtube_replay_command = "mm-youtubereplay " + saved_requests_path + " " + mahimahi_options + " " + browser_command + " --window-size=1920,1080 --ignore-certificate-errors --user-data-dir=/tmp/nonexistent$(date +%s%N) '" + url + "' 2> ./youtube_stall_logs/render_logs.txt"
	print youtube_replay_command
	print
	if os.system(youtube_replay_command):
		print "YouTube replay has failed. Try running sudo sysctl -w net.ipv4.ip_forward=1 if you have not done so already and make sure to check ./youtube_stall_logs/render_logs.txt for errors."
		sys.exit(1)
		

if __name__ == '__main__':
  main()
