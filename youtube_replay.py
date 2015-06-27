#!/usr/bin/python

# This script checks for mm-webrecord saved request/response pairs and
# also checks for media files in the directory for the youtube link. 

# The media files must be stored in a media_files directory and
# the mm-webrecord files must be stored in a saved_requests directory. 
# Note that these two directories are automatically created by 
# youtube_record.py. 

# USAGE: python youtube_replay.py youtube_url

def main():
	youtube_url = sys.argv[1]
	match_object = re.search("\?v=(.+)", youtube_url)
	video_id = ""
  	if not match_object:
  		print sys.argv[1] + " is not a valid youtube url" 
  		sys.exit()
  	else:
  		video_id = match_object.group(1)
  		print video_id 
	media_files_path =  os.path.dirname(os.path.realpath(__file__)) + "/media_files/" + video_id
	saved_requests_path = os.path.dirname(os.path.realpath(__file__)) + "/saved_requests/" + video_id
	if not os.path.exists(saved_requests_path): 
		print "ERROR: It appears you do not have any saved request response pairs for video id " + video_id
		print "These requests could not be found in " + saved_requests_path
		print "Please run python youtube_record.py " + youtube_url
		sys.exit()
	if not os.path.exists(media_files_path):
		print "ERROR: It appears you have downloaded the youtube video with video id " + video_id
		print "The downloaded media files could not be found in " + media_files_path
		print "Please run python youtube_record.py " + youtube_url
		sys.exit()
	os.system("mm-youtubereplay " + saved_requests_path + " chromium-browser --ignore-certificate-errors --user-data-dir=/tmp/nonexistent$(date +%s%N) " + youtube_url)
		

if __name__ == '__main__':
  main()
