#!/usr/bin/python

#Usage: python bulk_seek_stats.py youtube_logs_folder youtube_index_directory SSIM_index_directory output_directory

from __future__ import print_function
import numpy as np
import pylab
import os
import sys
import re
import collections
import pprint
import math
from decimal import *

def get_extended_plot_info(logfile_path):
    resolution_list = []
    time_list = []
    num_bytes_list = []
    time_first = -1
    time_last = -1
    most_bytes_requested = -1
    with open(logfile_path) as f:
        for line in f:
            resolution = re.search("[0-9]+x([0-9]+)", line)
            time = re.search("([0-9]+):([0-9]+):([0-9]+)", line)
            byte_range = re.search("([0-9]+)-([0-9]+)", line)
            month_day = re.search("([A-Z][a-z]{2}) ([A-Z][a-z]{2})  ?([0-9]+)", line)
            resolution_list.append(resolution.group(1))
            time_sec = (int(month_day.group(3)) * 86400 + int(time.group(1)) * 3600 + int(time.group(2)) * 60 + int(time.group(3)))
            time_list.append(time_sec)
            if time_first == -1:
                time_first = time_sec
            time_last = time_sec
            num_bytes = int(byte_range.group(2)) - int(byte_range.group(1))
            num_bytes_list.append(num_bytes)
            if(num_bytes > most_bytes_requested):
                most_bytes_requested = num_bytes
    return (resolution_list, time_list, num_bytes_list, time_first, time_last, most_bytes_requested)

def get_resolution_from_filename_sintel_1080(index_filename):
    match_object = re.search("818", index_filename)
    if match_object:
        return "818"
    match_object = re.search("546", index_filename)
    if match_object:
        return "546"
    match_object = re.search("364", index_filename)
    if match_object:
        return "364"
    match_object = re.search("274", index_filename)
    if match_object:
        return "274"
    match_object = re.search("182", index_filename)
    if match_object:
        return "182"
    match_object = re.search("110", index_filename)
    if match_object:
        return "110"
    raise ValueError("Can't sintel filename " + index_filename)


def get_resolution_from_filename_sintel_720(index_filename):
    match_object = re.search("544", index_filename)
    if match_object:
        return "544"
    match_object = re.search("362", index_filename)
    if match_object:
        return "362"
    match_object = re.search("272", index_filename)
    if match_object:
        return "272"
    match_object = re.search("182", index_filename)
    if match_object:
        return "182"
    match_object = re.search("108", index_filename)
    if match_object:
        return "108"
    raise ValueError("Can't sintel filename " + index_filename)

def get_plot_info(logfile_path):
    resolution_list = []
    byte_range_list = []
    with open(logfile_path) as f:
        for line in f:
            resolution = re.search("[0-9]+x([0-9]+)", line)
            byte_range = re.search("([0-9]+-[0-9]+)", line)
            resolution_list.append(resolution.group(1))
            byte_range_list.append(byte_range.group(1))
    return (resolution_list, byte_range_list)

def get_filenames_list(directory_path):
    filenames_list = []
    for dirpath,_,filenames in os.walk(directory_path):
        for f in filenames:
            filenames_list.append(os.path.abspath(os.path.join(dirpath, f)))
    return filenames_list

def get_time_range(byte_range, offset_list, time_last):
    split_array = byte_range.split("-")
    range_start = long(split_array[0])
    range_end = long(split_array[1])
    offset_index = 0
    while(offset_index != len(offset_list) and range_start >= long(offset_list[offset_index][0])):
        offset_index = offset_index + 1
    if offset_index != 0:
        start_time = offset_list[offset_index - 1][1]
    else:
        start_time = "0.0"
    offset_index = 0
    while(offset_index != len(offset_list) and range_end >= long(offset_list[offset_index][0])):
        offset_index = offset_index + 1
    if offset_index != len(offset_list):
        end_time = offset_list[offset_index][1]
    else:
        end_time = str(time_last)
    return (start_time, end_time)

def get_merged_time_ranges(graph_dict):
    final_graph_dict = collections.defaultdict(lambda: list())
    for resolution,time_range_list in graph_dict.iteritems():
        merged_time_range_list = merge_time_ranges(time_range_list)
        final_graph_dict[resolution] = merged_time_range_list
    return final_graph_dict

def merge_time_ranges(time_range_list):
    merged_time_range_list = []
    previous_range_start = -1
    previous_range_end = -1
    for (range_start, range_end) in time_range_list:
        if previous_range_start == -1 or previous_range_end == -1:
            previous_range_start = range_start
            previous_range_end = range_end
        elif previous_range_end >= range_start:
            previous_range_start = min(previous_range_start, range_start)
            previous_range_end = max(previous_range_end, range_end)
        else:
            merged_time_range_list.append((previous_range_start, previous_range_end))
            previous_range_start = range_start
            previous_range_end = range_end

    if previous_range_start != -1 and previous_range_end != -1:
        merged_time_range_list.append((previous_range_start, previous_range_end))
    return merged_time_range_list

def get_byte_range(time_range, time_byte_mapping):
    time_start = str(time_range[0])
    time_end = str(time_range[1])
    bytes_start = -1
    bytes_end = -1
    for mapping_tup in time_byte_mapping:
        if time_start == mapping_tup[1]:
            bytes_start = mapping_tup[0]
        if time_end == mapping_tup[1]:
            bytes_end = mapping_tup[0]
            break
    assert bytes_start is not -1
    assert bytes_end is not -1
    return (bytes_start, bytes_end)

def get_SSIM_scores_list(byte_range, SSIM_byte_mapping):
    SSIM_scores = []
    bytes_start = byte_range[0]
    bytes_end = byte_range[1]
    within_range = False
    for mapping_tup in SSIM_byte_mapping:
        if long(mapping_tup[0]) >= long(bytes_start) and long(mapping_tup[0]) <= long(bytes_end):
            within_range = True
        else:
            within_range = False
        if within_range:
            SSIM_scores.append(mapping_tup[1])
    return SSIM_scores

def mean_stddev(list_of_values):
    num_values = len(list_of_values)
    sum_values = 0.0
    for value in list_of_values:
        sum_values += float(value)
    mean = sum_values / num_values
    sum_square_error = 0.0
    for value in list_of_values:
        sum_square_error += math.pow(float(value) - mean, 2)
    stddev = math.sqrt(sum_square_error / num_values)
    return (mean, stddev)

def mean_stddev_min_SSIM(SSIM_graph_dict):
    SSIM_scores_data_points_list = list()
    for resolution,time_ssim_mapping_list in SSIM_graph_dict.iteritems():
        for time_range_ssim_tup in time_ssim_mapping_list:
            SSIM_scores_data_points_list += time_range_ssim_tup[1]
    (ssim_mean, ssim_stddev) = mean_stddev(SSIM_scores_data_points_list)
    return (ssim_mean, ssim_stddev, min(SSIM_scores_data_points_list))

def read_SSIM_index(index_directory):
    index = collections.defaultdict(lambda: list())
    filenames = get_filenames_list(index_directory)
    for filename in filenames:
        resolution = re.search("[0-9]+x([0-9]+)", filename).group(1)
        with open(filename) as index_file:
            for line in index_file:
                match_object = re.search("[0-9]+ ([0-9]+.[0-9]+) [A-Z] [0-9]+ ([0-9]+)", line)
                if match_object:
                    SSIM_score = match_object.group(1)
                    byte_offset = match_object.group(2)
                    index[resolution].append((byte_offset, SSIM_score))
    for resolution, index_tup in index.iteritems():
        index[resolution].sort(key=lambda tup: tup[0])
    return index

def get_SSIM_graph_dict(graph_dict, SSIM_dictionary, index):
    SSIM_graph_dict = collections.defaultdict(lambda: list())
    for resolution, time_range_list in graph_dict.iteritems():
        for time_range in time_range_list:
            byte_range = get_byte_range(time_range, index[resolution])
            SSIM_scores = get_SSIM_scores_list(byte_range, SSIM_dictionary[resolution])
            SSIM_graph_dict[resolution].append((time_range, SSIM_scores))
    return SSIM_graph_dict

def get_frames_displayed(stall_logfilename):
    frames_displayed = set()
    with open(stall_logfilename) as stall_logfile:
        previous_render_call_time = Decimal(0.0)
        previous_frame_presentation_time = ""
        for line in stall_logfile:
            match_object = re.search("RENDER CALL ON: ([0-9]+(?:\.[0-9]+)?)s TIME: (.+)", line)
            if match_object:
                render_call_time = Decimal(match_object.group(2))
                frame_presentation_time = match_object.group(1)
                frames_displayed.add(Decimal(frame_presentation_time))
    return frames_displayed

def time_ranges_from_frames_displayed(frames_displayed):
    time_ranges = []
    previous_presentation_time = 0.0
    current_range_start = 0.0
    for presentation_time in frames_displayed:
        presentation_time = float(presentation_time)
        if presentation_time - previous_presentation_time > 30.0:
            current_range_end = previous_presentation_time
            time_ranges.append((current_range_start, current_range_end))
            current_range_start = presentation_time
        previous_presentation_time = presentation_time
    time_ranges.append((current_range_start, previous_presentation_time))
    return time_ranges

def has_overlap(time_range1, time_range2):
    if(time_range1[0] > time_range2[0] and time_range1[0] < time_range2[1]):
        return True
    if(time_range1[1] > time_range2[0] and time_range1[1] < time_range2[1]):
        return True
    if(time_range2[0] > time_range1[0] and time_range2[0] < time_range1[1]):
        return True
    if(time_range2[1] > time_range1[0] and time_range2[1] < time_range1[1]):
        return True
    if(time_range2[0] == time_range1[0] and time_range2[1] == time_range1[1]):
        return True
    return False

def get_overlap_list(time_range, time_ranges_displayed):
    overlap_list = []
    for time_range_displayed in time_ranges_displayed:
        overlap_list.append(has_overlap(time_range, time_range_displayed))
    return overlap_list

def remove_overlap(time_range1, time_range2):
    return (max(time_range1[0], time_range2[0]), min(time_range1[1], time_range2[1]))

def trim_overlap(time_range, time_ranges_displayed):
    trimmed_time_ranges = []
    overlap_list = get_overlap_list(time_range, time_ranges_displayed)
    for i, has_overlap in enumerate(overlap_list):
        if has_overlap:
            trimmed_time_ranges.append(remove_overlap(time_range, time_ranges_displayed[i]))
    return trimmed_time_ranges

def trim_data_not_displayed(final_graph_dict, time_ranges_displayed):
    trimmed_graph_dict = collections.defaultdict(lambda: list())
    for resolution in final_graph_dict:
        time_range_list = final_graph_dict[resolution]
        for time_range in time_range_list:
            time_ranges = trim_overlap(time_range, time_ranges_displayed)
            trimmed_graph_dict[resolution] += time_ranges
    return trimmed_graph_dict

def time_range_list_has_overlap(time_range_list):
    for time_range_tup1 in time_range_list:
        time_range1 = time_range_tup1[1]
        for time_range_tup2 in time_range_list:
            time_range2 = time_range_tup2[1]
            if time_range_tup1[0] != time_range_tup2[0]:
                if has_overlap(time_range1, time_range2):
                    return True
    return False

def higher_stream_wins(resolution1, resolution2, time_range1, time_range2):
    if int(resolution1) > int(resolution2):
        return [(resolution1, time_range1)]
    else:
        new_time_ranges = []
        overlap_region = (max(time_range1[0], time_range2[0]), min(time_range1[1], time_range2[1]))
        if time_range1[0] < overlap_region[0]:
            new_time_ranges.append((resolution1, (time_range1[0], overlap_region[0])))
        if time_range1[1] > overlap_region[1]:
            new_time_ranges.append((resolution1, (overlap_region[1], time_range1[1])))
        return new_time_ranges

def remove_first_overlap(streams_list):
    first_overlap_indexes = (-1, -1)
    resolution1 = ""
    resolution2 = ""
    time_range1 = (-1, -1)
    time_range2 = (-1, -1)
    found_overlap = False
    for i1, time_range_tup1 in enumerate(streams_list):
        for i2, time_range_tup2 in enumerate(streams_list):
            if time_range_tup1[0] != time_range_tup2[0]:
                time_range1 = time_range_tup1[1]
                time_range2 = time_range_tup2[1]
                if has_overlap(time_range1, time_range2):
                    first_overlap_indexes = (i1, i2)
                    resolution1 = time_range_tup1[0]
                    resolution2 = time_range_tup2[0]
                    found_overlap = True
            if found_overlap:
                break
        if found_overlap:
            break
    streams_list.pop(i1)
    streams_list.pop(i2 - 1)
    streams_list += (higher_stream_wins(resolution1, resolution2, time_range1, time_range2))
    streams_list += (higher_stream_wins(resolution2, resolution1, time_range2, time_range1))
    streams_list.sort(key=lambda tup: tup[1][0])
    return streams_list

def remove_overlap_from_streams(final_graph_dict):
    final_graph_dict_without_overlap = collections.defaultdict(lambda: list())
    streams_list = []
    for stream in final_graph_dict:
        for time_range in final_graph_dict[stream]:
            streams_list.append((stream, time_range))
    streams_list.sort(key=lambda tup: tup[1][0])
    while(time_range_list_has_overlap(streams_list)):
        streams_list = remove_first_overlap(streams_list)
    for stream in streams_list:
        if stream[1][0] != -1:
            final_graph_dict_without_overlap[stream[0]].append(stream[1])
    return final_graph_dict_without_overlap

def get_SSIMs_new_time_range(SSIM_dict, time_range):
    SSIMs = []
    time_range_start = time_range[0]
    time_range_end = time_range[1]
    for SSIM_tup in SSIM_dict:
        time = SSIM_tup[0]
        SSIM = SSIM_tup[1]
        if time > time_range_start and time < time_range_end:
            SSIMs.append(SSIM)
    return SSIMs

def remove_overlapping_SSIM(SSIM_graph_dict, final_graph_dict):
    SSIM_dict = collections.defaultdict(lambda: list())
    for resolution in SSIM_graph_dict:
        for time_range_SSIM_tup in SSIM_graph_dict[resolution]:
            time_range = time_range_SSIM_tup[0]
            SSIMs = time_range_SSIM_tup[1]
            time_range_start = time_range[0]
            time_range_end = time_range[1]
            assert len(SSIMs) is not 0
            secs_per_frame = (time_range_end - time_range_start) / len(SSIMs)
            counter = 0
            time_range_curr = time_range_start
            while(time_range_curr < time_range_end and counter < len(SSIMs)):
                SSIM_dict[resolution].append((time_range_curr, SSIMs[counter]))
                time_range_curr = time_range_curr + secs_per_frame
                counter = counter + 1
    SSIM_graph_dict_without_overlap = collections.defaultdict(lambda: list())
    for resolution in final_graph_dict:
        for time_range in final_graph_dict[resolution]:
            SSIMs = get_SSIMs_new_time_range(SSIM_dict[resolution], time_range)
            SSIM_graph_dict_without_overlap[resolution].append((time_range, SSIMs))
    return SSIM_graph_dict_without_overlap

def get_media_index(index_directory, video_type):
    all_files = get_filenames_list(index_directory)
    index_filenames = []
    for filename in all_files:
        match_object = re.search("[0-9]+x[0-9]+_index", filename)
        if match_object:
            index_filenames.append(filename)
    time_last = -1
    index = collections.defaultdict(lambda: list()) #dictionary from resolution to sorted list of tuples (byte offset, time offset)
    for index_filename in index_filenames:
        resolution = ""
        if video_type == "1080":
            resolution = get_resolution_from_filename_sintel_1080(index_filename)
        else:
            resolution = get_resolution_from_filename_sintel_720(index_filename)
        with open(index_filename) as index_file:
            for line in index_file:
                offset_match_object = re.search("Byte Offset: ([0-9]+) Time Offset: ([0-9]+.[0-9]+)", line)
                if offset_match_object:
                    byte_offset = offset_match_object.group(1)
                    time_offset = offset_match_object.group(2)
                    index[resolution] = index[resolution] + [(byte_offset, time_offset)]
                duration_match_object = re.search("Duration: ([0-9]+)", line)
                if duration_match_object:
                    time_last = float(duration_match_object.group(1))/1000
    return (index, time_last)

def get_SSIM_data(logfile_path, index, SSIM_dictionary, stall_logfile, trial_id, output_directory, time_last):
    plotTuple = get_plot_info(logfile_path)
    resolution_list = plotTuple[0]
    byte_range_list = plotTuple[1]
    final_graph_dict = collections.defaultdict(lambda: list())
    for i,resolution_requested in enumerate(resolution_list):
        offset_list = index[resolution_requested]
        time_range = get_time_range(byte_range_list[i], offset_list, time_last)
        if(time_range[0] != "0.0" or time_range[1] != "0.0"):
            time_tuple = (float(time_range[0]), float(time_range[1]))
            final_graph_dict[resolution_requested] = final_graph_dict[resolution_requested] + [time_tuple]
    final_graph_dict = get_merged_time_ranges(final_graph_dict)
    SSIM_graph_dict = get_SSIM_graph_dict(final_graph_dict, SSIM_dictionary, index)
    frames_displayed = list(get_frames_displayed(stall_logfile))
    frames_displayed.sort()
    time_ranges_displayed = time_ranges_from_frames_displayed(frames_displayed)
    final_graph_dict = trim_data_not_displayed(final_graph_dict, time_ranges_displayed)
    final_graph_dict = remove_overlap_from_streams(final_graph_dict)
    SSIM_graph_dict = remove_overlapping_SSIM(SSIM_graph_dict, final_graph_dict)
    (mean_SSIM, stddev_SSIM, min_SSIM) = mean_stddev_min_SSIM(SSIM_graph_dict)
    return (mean_SSIM, stddev_SSIM, min_SSIM)

def main():
    if len( sys.argv ) is not 6:
        raise ValueError("Usage: python raster-SSIM-scores.py youtube_logs_folder youtube_index_directory SSIM_index_directory output_directory 1080/720")
    logs_folder = sys.argv[1]
    index_directory = sys.argv[2]
    SSIM_index_directory = sys.argv[3]
    output_directory = sys.argv[4]
    video_type = sys.argv[5]
    SSIM_dictionary = read_SSIM_index(SSIM_index_directory)
    (media_index, time_last) = get_media_index(index_directory, video_type)
    if not os.path.exists(output_directory):
        os.system("mkdir " + output_directory)
    files_list = list()
    for dirpath,_,filenames in os.walk(logs_folder):
        for f in filenames:
            files_list.append(os.path.abspath(os.path.join(dirpath, f)))
    id_to_logfiles = collections.defaultdict(lambda: {})
    for filepath in files_list:
        stall_logfile_match_object = re.search("stall-log-(.+).txt", filepath)
        if stall_logfile_match_object:
            stall_logfile_match_id = stall_logfile_match_object.group(1)
            id_to_logfiles[stall_logfile_match_id]["stalls"] = filepath
        else:
            quality_logfile_match_object = re.search("log-(.+).txt", filepath)
            if quality_logfile_match_object:
                quality_logfile_id = quality_logfile_match_object.group(1)
                id_to_logfiles[quality_logfile_id]["quality"] = filepath
    SSIM_dict = collections.defaultdict(lambda: (0.0, 0.0))
    mean_SSIM_list = list()
    min_SSIM_list = list()
    for trial_id in id_to_logfiles:
        logfiles = id_to_logfiles[trial_id]
        assert len(logfiles) is 2, "trial %s missing log files. Has: %s" % (trial_id, str(logfiles))
    for trial_id in id_to_logfiles:
        logfiles = id_to_logfiles[trial_id]
        quality_logfile = logfiles["quality"]
        stall_logfile = logfiles["stalls"]
        (mean_SSIM, stddev_SSIM, min_SSIM) = get_SSIM_data(quality_logfile, media_index, SSIM_dictionary, stall_logfile, trial_id, output_directory, time_last)
        SSIM_dict[trial_id] = (mean_SSIM, stddev_SSIM, min_SSIM)
        mean_SSIM_list.append(mean_SSIM)
        min_SSIM_list.append(min_SSIM)
    SSIM_mean_stddev_output_filename = output_directory + "/mean_stddev_SSIM.txt"
    SSIM_mean_stddev_output_file = open(SSIM_mean_stddev_output_filename, 'w')
    (mean_of_mean_SSIM, stddev_across_mean_SSIM) = mean_stddev(mean_SSIM_list)
    print("Standard Deviation Across SSIM Means: " + str(stddev_across_mean_SSIM), file=SSIM_mean_stddev_output_file)
    (mean_of_min_SSIM, stddev_across_min_SSIM) = mean_stddev(min_SSIM_list)
    print("Mean Across Minimum SSIMs: " + str(mean_of_min_SSIM), file=SSIM_mean_stddev_output_file)
    print("Standard Deviation Across Minimum SSIMs: " + str(stddev_across_min_SSIM), file=SSIM_mean_stddev_output_file)
    for trial_id in SSIM_dict:
        print("Trial " + trial_id + ":", file=SSIM_mean_stddev_output_file)
        (mean_SSIM, stddev_SSIM, min_SSIM) = SSIM_dict[trial_id]
        print("\tMean SSIM: " + str(mean_SSIM), file=SSIM_mean_stddev_output_file)
        print("\tStdDev SSIM: " + str(stddev_SSIM), file=SSIM_mean_stddev_output_file)
        print("\tMinimum SSIM: " + str(min_SSIM), file=SSIM_mean_stddev_output_file)



if __name__ == '__main__':
  main()
