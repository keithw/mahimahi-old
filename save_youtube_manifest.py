#!/usr/bin/python

# This script saves the youtube manifest (mpeg-dash mpd) for a youtube video. 

# USAGE: python save_youtube_manifest.py 'youtube_url'

import sys
import subprocess
import re
import os

def main():
    youtube_url = sys.argv[1]
    match_object = re.search("/embed/([_a-zA-Z0-9\-]+)", youtube_url)
    video_id = ""
    if not match_object:
        print "ERROR: " + youtube_url + " is not a valid embed youtube url"
        will_provide_video_id = get_yes_or_no("Would you like to provide a video id for your custom url? y/n\n")
        if will_provide_video_id:
            video_id = raw_input("Please provide the video id in the terminal...\n")
            youtube_url = "https://www.youtube.com/embed/" + video_id
        else:
            print "Without a video id we cannot download your video from YouTube. Either use a correctly formatted YouTube embed url or provide a video id for your custom url."
            sys.exit(1)
    else:
        video_id = match_object.group(1)
    if not os.path.exists("./manifests"):
        os.system("mkdir ./manifests")
    manifest_filename = "./manifests/" + video_id + ".xml"
    os.system("curl $(youtube-dl " + youtube_url + " --youtube-include-dash-manifest --dump-intermediate-pages -s | grep manifest.google | cut -d ' ' -f 5) > " + manifest_filename)
    print "Manifest for " + youtube_url + " saved to " + manifest_filename

if __name__ == '__main__':
  main()
