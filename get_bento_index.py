#!/usr/bin/python

#Usage: python get_bento_index.py 'youtube_url'

from __future__ import print_function
import sys
import re
import os
from os import walk
import subprocess
import shutil


def delete_filesys_subtree(root_directory):
	for the_file in os.listdir(root_directory):
	    file_path = os.path.join(root_directory, the_file)
	    try:
	        if os.path.isfile(file_path):
	            os.unlink(file_path)
	        elif os.path.isdir(file_path): shutil.rmtree(file_path)
	    except Exception, e:
	        print(e)

def get_media_filenames_list(media_files_path):
	media_files_list = []
	for dirpath,_,filenames in os.walk(media_files_path):
		for f in filenames:
			media_files_list += [os.path.abspath(os.path.join(dirpath, f))]
	return media_files_list

def main():
	if not os.path.exists("./media_indexes"):
		os.makedirs("./media_indexes")
	youtube_url = sys.argv[1]
  	match_object = re.search("/embed/([_a-zA-Z0-9\-]+)", youtube_url)
  	video_id = ""
	if not match_object:
		print("ERROR: " + youtube_url + " is not a valid embed youtube url") 
		sys.exit()
  	else:
  		video_id = match_object.group(1)
  		input_media_files_path =  os.path.dirname(os.path.realpath(__file__)) + "/media_files/" + video_id
  		output_index_path = os.path.dirname(os.path.realpath(__file__)) + "/media_indexes/" + video_id
  		if os.path.exists(output_index_path):
  			delete_filesys_subtree(output_index_path)
  			shutil.rmtree(output_index_path)
		os.makedirs(output_index_path)
		os.makedirs(output_index_path + "/audio")
		os.makedirs(output_index_path + "/video")
		os.makedirs(output_index_path + "/audio/mp4")
		os.makedirs(output_index_path + "/video/mp4")
		os.makedirs(output_index_path + "/video/webm")
		os.makedirs(output_index_path + "/audio/webm")
  		media_filenames_list = get_media_filenames_list(input_media_files_path)
		for media_filename in media_filenames_list:
			file_extension = media_filename.split(input_media_files_path, 1)[1]
			bento_command = "../bento/bin/mp4dump " + media_filename + " > " + output_index_path + file_extension + "_mp4dump"
			proc = subprocess.Popen(bento_command, stdout=subprocess.PIPE, shell=True)
		 	(out, err) = proc.communicate()
		 	if proc.returncode:
	  			print("The Bento tool seems to have failed. Please fix the errors and run the script again.")
	  			sys.exit(1)
		mp4dump_filenames_list = get_media_filenames_list(output_index_path)
		for mp4dump_filename in mp4dump_filenames_list:
			index_file_name = mp4dump_filename.split("_mp4dump", 1)[0] + "_index"
			index_file = open(index_file_name, 'w')
			with open(mp4dump_filename) as mp4dump_file:
				timescale = -1
				duration = -1
				sequence_number = -1
				time_offset = -1
				saved_byte_offset = -1
				byte_offset = 0
				for line in mp4dump_file:
					duration_match_object = re.search("duration\(ms\) = ([0-9]+)", line)
					if duration_match_object:
						duration = duration_match_object.group(1)
						print("Duration: " + duration, file=index_file)
					moof_match_object = re.search("\[moof\]", line)
					if moof_match_object:
						saved_byte_offset = byte_offset
					mdat_match_object = re.search("\[mdat\]", line)
					if mdat_match_object:
						print("Byte Offset: " + str(saved_byte_offset) + " Time Offset: " + str(float(time_offset)/float(timescale)), file=index_file)
					timescale_match_object = re.search("timescale = ([0-9]+)", line)
					if timescale_match_object:
						#print timescale_match_object.group(1)
						timescale = timescale_match_object.group(1)
					duration_match_object = re.search("  duration = ([0-9]+)", line)
					if duration_match_object:
						duration = duration_match_object.group(1)
					sequence_number_match_object = re.search("sequence number = ([0-9]+)", line)
					if sequence_number_match_object:
						sequence_number = sequence_number_match_object.group(1)
					size_match_object = re.match("\[[a-z]+\] size=([0-9]+\+[0-9]+)", line)
					if size_match_object:
						sizes_array = size_match_object.group(1).split("+")
						total_size = int(sizes_array[0]) + int(sizes_array[1])
						byte_offset = byte_offset + total_size
					time_offset_match_object = re.search("base media decode time = ([0-9]+)", line)
					if time_offset_match_object:
						time_offset = time_offset_match_object.group(1)
				print("Byte Offset: " + str(byte_offset) + " Time Offset: " + str(float(duration)/float(1000)), file=index_file)

if __name__ == '__main__':
  main()