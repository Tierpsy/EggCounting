#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 12:10:43 2020

@author: lferiani
"""

import re
import fire
import tables
import imgstore
import numpy as np
from tqdm import tqdm
from pathlib import Path
from collections import defaultdict

TIMELAPSE_REGEXP = r"\_\d{4}\_20\d{6}_\d{6}"
CAMERA_REGEXP = r"(?<=20\d{6}\_\d{6}\.)\d{8}"
TIMEPOINT_REGEXP = r"(?<=\_)\d{4}(?=\_20\d{6}\_\d{6}\.\d{8})"
TABLE_FILTERS = tables.Filters(
        complevel=5,
        complib='zlib',
        shuffle=True,
        fletcher32=True)


def parse_camera_serial(filename):
    camera_serial = re.findall(CAMERA_REGEXP, str(filename).lower())[0]
    return camera_serial


def parse_timepoint_number(filename):
    timepoint_number = re.findall(TIMEPOINT_REGEXP, str(filename).lower())[0]
    return int(timepoint_number)


def find_timelapse_imgstores(working_dir):
    """
    Scan the working directory looking for imgstores with a file pattern
    matching _0000_YYYYMMDD_HHMMSS
    """
    fnames = working_dir.rglob('metadata.yaml')
    # filter to return only files matching the right pattern
    fnames = [f for f in fnames if re.search(TIMELAPSE_REGEXP, f.parent.name)]

    return fnames


def sort_timelapse_imgstores(paths_gen):
    """
    Split the list of all imgstores into a dictionary of sorted lists
    Keys are the camera serials, and values their list of timepoints
    """
    # split imgstores according to their camera serial
    timelapses_dict = defaultdict(list)
    for fname in paths_gen:
        camera_serial = parse_camera_serial(fname)
        timelapses_dict[camera_serial].append(fname)
    # now sort each list
    for serial in timelapses_dict.keys():
        timelapses_dict[serial].sort()

    return timelapses_dict


def get_firstframe(imgstore_fname):
    store = imgstore.new_for_filename(str(imgstore_fname))
    img = store.get_next_image()[0]
    store.close()
    return img


def get_frame_size(imgstore_fname):
    store = imgstore.new_for_filename(str(imgstore_fname))
    im_height, im_width = store._imgshape
    store.close()
    return im_height, im_width


def timepoint_to_frame(fname, mode='first'):
    """
    Generate a single image from a short timepoint video,
    by taking the first frame only.
    TODO: implement to instead take the average, or max or min projection
    """
    if mode != 'first':
        raise Exception(f'{mode} not coded yet')
    else:
        timepoint_frame = get_firstframe(fname)
    return timepoint_frame


def init_dataset(fid, tot_frames, im_height, im_width, is_expandable=True):

    img_dataset = fid.create_earray(
        '/',
        'full_data',
        atom=tables.UInt8Atom(),
        shape=(0, im_height, im_width),
        chunkshape=(1, im_height, im_width),
        expectedrows=tot_frames,
        filters=TABLE_FILTERS
        )

    return img_dataset


def make_output_fname(first_timepoint_fname):
    out_name = first_timepoint_fname.parent
    out_name = str(out_name).replace(
        'RawVideos', 'Timelapses'
        ).replace('_0000_', '_')
    out_name += '_timelapse.hdf5'
    out_name = Path(out_name)
    return out_name


def process_timepoints(timepoints_fnames):
    """
    Loop over the files in the list, collect frames, concatenate, write out
    """
    n_frames = len(timepoints_fnames)
    im_height, im_width = get_frame_size(timepoints_fnames[0])
    buffer_size = 10
    # get name for output file
    output_fname = make_output_fname(timepoints_fnames[0])
    output_fname.parent.mkdir(exist_ok=True, parents=True)
    if output_fname.exists():
        return

    # loop and write
    with tables.File(output_fname, 'w') as out_fid:
        # initialise dataset to write in
        dataset = init_dataset(out_fid, n_frames, im_height, im_width)
        # create empty frame buffer
        frame_buffer = []
        for fc, fname in enumerate(tqdm(timepoints_fnames)):
            # get frame and append to buffer
            frame = timepoint_to_frame(fname)[None, :, :]
            frame_buffer.append(frame)
            # if buffer is full, or last frame read, write buffer
            if (fc+1 % buffer_size == 0) or (fc+1 == n_frames):
                frame_buffer = np.concatenate(frame_buffer, axis=0)
                dataset.append(frame_buffer)
                frame_buffer = []
        # write attributes
        attr_writer = getattr(dataset, '_v_attrs')
        attr_writer['microns_per_pixel'] = 12.4
        attr_writer['expected_fps'] = 1
        attr_writer['time_units'] = 'frames'
        attr_writer['xy_units'] = 'micrometers'
        attr_writer["CLASS"] = np.string_("IMAGE")
        attr_writer["IMAGE_SUBCLASS"] = np.string_("IMAGE_GRAYSCALE")
        attr_writer["IMAGE_WHITE_IS_ZERO"] = np.array(0, dtype="uint8")
        attr_writer["DISPLAY_ORIGIN"] = np.string_("UL")  # not rotated
        attr_writer["IMAGE_VERSION"] = np.string_("1.2")

    return


def make_timelapses_from_folder(rawvideos_day_dir):
    """
    Scan the input folder for imgstore raw videos, looking for timepoints
    to stitch into a timelapsed video.
    Group the timepoints into lists, one per each camera serial.
    Stitch the time points from the same camera into a file with structure
    compatible with a Tierpsy's masked video (but only /full_data, no /mask

    Parameters
    ----------
    rawvideos_day_dir : path or str
        Path to a day's subfolder in a RawVideos folder.

    Returns
    -------
    None.

    """
    if isinstance(rawvideos_day_dir, str):
        rawvideos_day_dir = Path(rawvideos_day_dir)
    assert rawvideos_day_dir.name != 'RawVideos', (
        'Input a day directory, not the whole RawVideos one')

    # find all imgstores
    print('Looking for suitable videos...')
    imgstore_list = find_timelapse_imgstores(rawvideos_day_dir)
    # reorganise them
    timepoints_dict = sort_timelapse_imgstores(imgstore_list)
    print(
        f'Found videos from {len(list(timepoints_dict.keys()))} cameras')
    # loop over cameras and stitch
    for camera_serial in timepoints_dict.keys():
        print(f'\nProcessing camera {camera_serial}')
        process_timepoints(timepoints_dict[camera_serial])
    return


def main():
    fire.Fire(make_timelapses_from_folder)


if __name__ == '__main__':
    main()
    # for testing:
    # rawvideos_dir = Path(
    #     '/Volumes/behavgenom$/Bonnie/Egg_laying_drug_screen/RawVideos/20201112')
    # make_timelapses_from_folder(rawvideos_dir)
