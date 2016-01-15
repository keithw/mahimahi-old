#!/usr/bin/python

#Usage: python bulk_seek_stats.py youtube_logs_folder youtube_index_directory SSIM_index_directory output_directory

from __future__ import print_function
import matplotlib
matplotlib.use('pdf') # Must be before importing matplotlib.pyplot or pylab! Default uses x window manager and won't work cleanly in cloud installations.
from matplotlib import collections
import numpy as np
import pylab
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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

def plot_resolution(logfile_path, output_filename):
    plot_tuple = get_extended_plot_info(logfile_path)
    resolution_list = plot_tuple[0]
    time_list = plot_tuple[1]
    time_first = plot_tuple[3]
    time_last = plot_tuple[4]
    time_last_adjusted = time_last - time_first
    time_list_adjusted = []
    s = []
    for i in range(0, len(time_list)):
        time_list_adjusted.append(time_list[i] - time_first)
        s.append(5)
    plt.scatter(time_list_adjusted, resolution_list, s=s, color="blue")
    plt.xlabel('time of data request in seconds')
    plt.ylabel('resolution')
    plt.ylim([0, 818])
    plt.xlim([-50, time_last_adjusted + 50])
    plt.savefig(output_filename)
    plt.clf()

def configure_file_system(logfile_path):
    trial_name = "unknown_trial_name"
    if not os.path.exists("./youtube_analysis_output"):
        os.system("mkdir youtube_analysis_output")
    trial_name_match_object = re.search("\.?\/?youtube_logs/([0-9A-Za-z_-]+)\.?(?:[A-Za-z]+)?", logfile_path)
    if trial_name_match_object:
        trial_name = trial_name_match_object.group(1)
    else:
        trial_name_match_object = re.search(".+\/([0-9A-Za-z_-]+)\.txt", logfile_path)
        if trial_name_match_object:
            trial_name = trial_name_match_object.group(1)
    output_filename = "./youtube_analysis_output/" + trial_name + "/"
    if not os.path.exists(output_filename):
        os.system("mkdir " + output_filename)
    return output_filename

def get_resolution_from_filename_sintel(index_filename):
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

def get_full_track_name(index_filename):
    match_object = re.search("818", index_filename)
    if match_object:
        return "1920x818"
    match_object = re.search("546", index_filename)
    if match_object:
        return "1280x546"
    match_object = re.search("364", index_filename)
    if match_object:
        return "854x364"
    match_object = re.search("274", index_filename)
    if match_object:
        return "640x274"
    match_object = re.search("182", index_filename)
    if match_object:
        return "426x182"
    match_object = re.search("110", index_filename)
    if match_object:
        return "256x110"
    raise ValueError("Can't read track name from index filename " + index_filename)

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

def plot_resolution_lines(graph_dict, time_first, time_last, output_filename):
    for resolution,time_range_list in graph_dict.iteritems():
        for time_range in time_range_list:
            plt.plot([time_range[0], time_range[1]], [resolution, resolution], color='Blue', linestyle='-', linewidth=1)
    plt.xlabel('time within video in seconds (with seeks)')
    plt.ylabel('resolution')
    plt.ylim([0, 818])
    plt.xlim([time_first - 100, time_last + 100])
    plt.savefig(output_filename)
    plt.clf()

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
    previous_time_range = (previous_range_start, previous_range_end)
    for time_range in time_range_list:
        range_start = time_range[0]
        range_end = time_range[1]
        if previous_range_start == -1 or previous_range_end == -1:
            previous_range_start = range_start
            previous_range_end = range_end
            previous_time_range = (previous_range_start, previous_range_end)
        elif previous_range_end >= range_start:
            previous_time_range = (min(previous_range_start, range_start), max(previous_range_end, range_end))
            previous_range_start = previous_time_range[0]
            previous_range_end = previous_time_range[1]
        else:
            merged_time_range_list.append(previous_time_range)
            previous_time_range = time_range
            previous_range_start = previous_time_range[0]
            previous_range_end = previous_time_range[1]
    if previous_range_start != -1 and previous_range_end != -1:
        merged_time_range_list.append(previous_time_range)
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

def mean_stddev_SSIM(SSIM_graph_dict):
    SSIM_scores_data_points_list = list()
    for resolution,time_ssim_mapping_list in SSIM_graph_dict.iteritems():
        for time_range_ssim_tup in time_ssim_mapping_list:
            SSIM_scores_data_points_list += time_range_ssim_tup[1]
    num_ssim_scores = len(SSIM_scores_data_points_list)
    sum_ssim_scores = 0.0
    for ssim_score in SSIM_scores_data_points_list:
        sum_ssim_scores += float(ssim_score)
    ssim_mean = sum_ssim_scores/num_ssim_scores
    sum_ssim_mean_square_error = 0.0
    for ssim_score in SSIM_scores_data_points_list:
        sum_ssim_mean_square_error += math.pow(float(ssim_score) - ssim_mean, 2)
    stddev = math.sqrt(sum_ssim_mean_square_error / num_ssim_scores)
    return (ssim_mean, stddev)

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

def plot_SSIM_graph(SSIM_graph_dict, time_first, time_last, output_filename):
    FRAMES_PER_SECOND = 24
    SAMPLE_SIZE = 1.0/24.0
    SSIM_scores_data_points_list = list()
    time_data_points_list = list()
    sorted_SSIM_mapping = list()
    for resolution,time_ssim_mapping_list in SSIM_graph_dict.iteritems():
        sorted_SSIM_mapping += time_ssim_mapping_list
    sorted_SSIM_mapping.sort(key=lambda tup: tup[0][0])
    size_list = []
    for time_ssim_mapping_tup in sorted_SSIM_mapping:
        time_range = time_ssim_mapping_tup[0]
        SSIM_scores = time_ssim_mapping_tup[1]
        total_time = float(time_range[1]) - float(time_range[0])
        time_range_beg = time_range[0]
        time_range_end = time_range_beg + SAMPLE_SIZE
        while(time_range_end <= float(time_range[1])):
            ssim_list_index = int((time_range_beg - time_range[0]) * FRAMES_PER_SECOND)
            if ssim_list_index >= len(SSIM_scores):
                break
            ssim_sum = 0.0
            num_ssim_scores = 0
            for i in range(ssim_list_index, ssim_list_index + int(FRAMES_PER_SECOND * SAMPLE_SIZE)):
                if i < len(SSIM_scores):
                    ssim_sum += float(SSIM_scores[i])
                    num_ssim_scores += 1
            average_ssim_score = ssim_sum / float(num_ssim_scores)
            SSIM_scores_data_points_list.append(average_ssim_score)
            time_data_points_list.append(time_range_end)
            time_range_beg += SAMPLE_SIZE
            time_range_end += SAMPLE_SIZE
            size_list.append(0.25)
    plt.scatter(time_data_points_list, SSIM_scores_data_points_list, color='Blue', s=size_list)
    plt.xlabel('time within video in seconds (with seeks)')
    plt.ylabel('SSIM score')
    plt.ylim([0.3, 1.05])
    plt.xlim([time_first - 100, time_last + 100])
    plt.savefig(output_filename)
    plt.clf()

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

def get_stall_data(stall_logfilename, trial_id, output_directory):
    frame_list = list()
    frame_set = set()
    stall_dict = collections.defaultdict(lambda: Decimal(0.0))
    stall_length_list = list()
    stall_presentation_time = list()
    stall_list = list()
    with open(stall_logfilename) as stall_logfile:
        previous_render_call_time = Decimal(0.0)
        previous_frame_presentation_time = ""
        for line in stall_logfile:
            match_object = re.search("RENDER CALL ON: ([0-9]+(?:\.[0-9]+)?)s TIME: (.+)", line)
            if match_object:
                render_call_time = Decimal(match_object.group(2))
                frame_presentation_time = match_object.group(1)
                if not frame_presentation_time in frame_set:
                    frame_list.append(frame_presentation_time)
                    frame_set.add(frame_presentation_time)
                if previous_render_call_time == 0:
                    previous_render_call_time = render_call_time
                    previous_frame_presentation_time = frame_presentation_time
                if render_call_time - previous_render_call_time > 0.018: #render calls occur every 17milliseconds or so
                    stall_dict[previous_frame_presentation_time] += render_call_time - previous_render_call_time - Decimal(0.017)
                    stall_length_list.append(render_call_time - previous_render_call_time)
                    stall_presentation_time.append(Decimal(frame_presentation_time))
                    stall_list.append((render_call_time - previous_render_call_time, Decimal(frame_presentation_time)))
                else:
                    stall_length_list.append(0)
                    stall_presentation_time.append(Decimal(frame_presentation_time))
                previous_render_call_time = render_call_time
                previous_frame_presentation_time = frame_presentation_time
    previous_time = 0
    previous_time_so_far = list()
    length_list_so_far = list()
    for i, time in enumerate(stall_presentation_time):
        if time - previous_time > 30:
            plt.plot(previous_time_so_far, length_list_so_far, color="blue")
            previous_time_so_far = list()
            length_list_so_far = list()
        previous_time_so_far.append(time)
        length_list_so_far.append(stall_length_list[i])
        previous_time = time
    plt.plot(previous_time_so_far, length_list_so_far, color="blue")
    plt.xlabel('Time in video (seconds)')
    plt.ylabel('Stall duration (seconds)')
    plt.ylim([-2, 20])
    plt.xlim([-30, 920])
    plt.savefig(output_directory + "/" + trial_id + "/" + "stalls.pdf")
    plt.clf()
    print_stall_list(stall_list, output_directory, trial_id)
    return stall_list

def print_stall_list(stall_list, output_directory, trial_id):
    stall_data_filename = output_directory + "/" + trial_id + "/" + "stall_data.dat"
    stall_data_file = open(stall_data_filename, 'w')
    for stall in stall_list:
        print("Stall length " + str(stall[0]) + "s before media time " + str(stall[1]) + "s", file=stall_data_file)

def print_track_dict(track_dict, output_directory, trial_id):
    track_data_filename = output_directory + "/" + trial_id + "/" + "track_data.dat"
    track_data_file = open(track_data_filename, 'w')
    for track in track_dict:
        print("Track: " + get_full_track_name(track), file=track_data_file)
        time_ranges = track_dict[track]
        for time_range in time_ranges:
            print("\t" + str(time_range[0]) + "s - " + str(time_range[1]) + "s", file=track_data_file)

def print_SSIM_dict(SSIM_dict, output_directory, trial_id):
    SSIM_data_filename = output_directory + "/" + trial_id + "/" + "SSIM_data.dat"
    SSIM_data_file = open(SSIM_data_filename, 'w')
    for track in SSIM_dict:
        print("Track: " + get_full_track_name(track), file=SSIM_data_file)
        for time_range_SSIM_tup in SSIM_dict[track]:
            time_range = time_range_SSIM_tup[0]
            print("\t" + str(time_range[0]) + "s - " + str(time_range[1]) + "s", file=SSIM_data_file)
            SSIM_list = time_range_SSIM_tup[1]
            for SSIM in SSIM_list:
                print("\t\t\t" + str(SSIM), file=SSIM_data_file)

def get_media_index(index_directory):
    all_files = get_filenames_list(index_directory)
    index_filenames = []
    for filename in all_files:
        match_object = re.search("[0-9]+x[0-9]+_index", filename)
        if match_object:
            index_filenames.append(filename)
    time_last = -1
    index = collections.defaultdict(lambda: list()) #dictionary from resolution to sorted list of tuples (byte offset, time offset)
    for index_filename in index_filenames:
        resolution = get_resolution_from_filename_sintel(index_filename)
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
    plot_resolution(logfile_path, output_directory + "/" + trial_id + "/" + "track_requests.pdf")
    plotTuple = get_plot_info(logfile_path)
    resolution_list = plotTuple[0]
    byte_range_list = plotTuple[1]
    final_graph_dict = collections.defaultdict(lambda: list())
    for i,resolution_requested in enumerate(resolution_list):
        offset_list = index[resolution_requested]
        time_range = get_time_range(byte_range_list[i], offset_list, time_last)
        #print "Resolution: " + resolution_requested + " Byte Range: " + byte_range_list[i] + " Time Range: " + str(time_range[0]) + "-" + str(time_range[1])
        if(time_range[0] != "0.0" or time_range[1] != "0.0"):
            time_tuple = (float(time_range[0]), float(time_range[1]))
            final_graph_dict[resolution_requested] = final_graph_dict[resolution_requested] + [time_tuple]
    final_graph_dict = get_merged_time_ranges(final_graph_dict)
    SSIM_graph_dict = get_SSIM_graph_dict(final_graph_dict, SSIM_dictionary, index)
    plot_resolution_lines(final_graph_dict, 0, time_last, output_directory + "/" + trial_id + "/" + "tracks_requested_mapped_to_media_time.pdf")
    frames_displayed = list(get_frames_displayed(stall_logfile))
    frames_displayed.sort()
    time_ranges_displayed = time_ranges_from_frames_displayed(frames_displayed)
    final_graph_dict = trim_data_not_displayed(final_graph_dict, time_ranges_displayed)
    plot_resolution_lines(final_graph_dict, 0, time_last, output_directory + "/" + trial_id + "/" + "tracks_rendered_to_media_time_including_overlap.pdf")
    final_graph_dict = remove_overlap_from_streams(final_graph_dict)
    plot_resolution_lines(final_graph_dict, 0, time_last, output_directory + "/" + trial_id + "/" + "tracks_rendered_to_media_time_no_overlap.pdf")
    print_track_dict(final_graph_dict, output_directory, trial_id)
    SSIM_graph_dict = remove_overlapping_SSIM(SSIM_graph_dict, final_graph_dict)
    plot_SSIM_graph(SSIM_graph_dict, 0, time_last, output_directory + "/" + trial_id + "/" + "SSIM_to_media_time_no_overlap.pdf")
    print_SSIM_dict(SSIM_graph_dict, output_directory, trial_id)
    (mean_SSIM, stddev_SSIM) = mean_stddev_SSIM(SSIM_graph_dict)
    stats_filename = output_directory + "/" + trial_id + "/" + "stats.txt"
    stats_file = open(stats_filename, 'w')
    print("Mean SSIM score: " + str(mean_SSIM), file=stats_file)
    print("Standard Deviation of SSIM scores: " + str(stddev_SSIM), file=stats_file)
    return (mean_SSIM, stddev_SSIM)


def main():
    if len( sys.argv ) is not 5:
        raise ValueError("Usage: python bulk_seek_stats.py youtube_logs_folder youtube_index_directory SSIM_index_directory output_directory")
    logs_folder = sys.argv[1]
    index_directory = sys.argv[2]
    SSIM_index_directory = sys.argv[3]
    output_directory = sys.argv[4]
    SSIM_dictionary = read_SSIM_index(SSIM_index_directory)
    (media_index, time_last) = get_media_index(index_directory)
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
    means_list = list()
    for trial_id in id_to_logfiles:
        logfiles = id_to_logfiles[trial_id]
        assert len(logfiles) is 2, "trial %s missing log files. Has: %s" % (trial_id, str(logfiles))
    for trial_id in id_to_logfiles:
        if os.path.exists(output_directory + "/" + trial_id):
            os.system("rm -rf " + output_directory + "/" + trial_id)
        os.system("mkdir " + output_directory + "/" + trial_id)
        print("Running analysis on trial: " + trial_id)
        logfiles = id_to_logfiles[trial_id]
        quality_logfile = logfiles["quality"]
        stall_logfile = logfiles["stalls"]
        print("\tQuality logfile: " + quality_logfile)
        print("\tStall logfile: " + stall_logfile)
        print ("getting ssim data..")
        (mean_SSIM, stddev_SSIM) = get_SSIM_data(quality_logfile, media_index, SSIM_dictionary, stall_logfile, trial_id, output_directory, time_last)
        SSIM_dict[trial_id] = (mean_SSIM, stddev_SSIM)
        print ("getting stall data..")
        stalls_list = get_stall_data(stall_logfile, trial_id, output_directory)
        means_list.append(mean_SSIM)
    SSIM_mean_stddev_output_filename = output_directory + "/mean_stddev_SSIM.txt"
    SSIM_mean_stddev_output_file = open(SSIM_mean_stddev_output_filename, 'w')
    num_means = len(means_list)
    sum_means = 0.0
    for mean in means_list:
        sum_means += float(mean)
    mean_of_means = sum_means / num_means
    sum_means_square_error = 0.0
    for mean in means_list:
        sum_means_square_error += math.pow(float(mean) - mean_of_means, 2)
    stddev_across_means = math.sqrt(sum_means_square_error / num_means)
    print("Standard Deviation Across SSIM Means: " + str(stddev_across_means), file=SSIM_mean_stddev_output_file)
    for trial_id in SSIM_dict:
        print("Trial " + trial_id + ":", file=SSIM_mean_stddev_output_file)
        (mean_SSIM, stddev_SSIM) = SSIM_dict[trial_id]
        print("\tMean SSIM: " + str(mean_SSIM), file=SSIM_mean_stddev_output_file)
        print("\tStdDev SSIM: " + str(stddev_SSIM), file=SSIM_mean_stddev_output_file)



if __name__ == '__main__':
  main()
