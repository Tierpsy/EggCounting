#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 14:04:17 2020

@author: lferiani

tool to add fov_wells to an hdf5 file that doesn't have any,
and to add well_name as a column to egg clicking data
"""

import fire
import pandas as pd
from tqdm import tqdm
from pathlib import Path

from eggcounting.split_fov.FOVMultiWellsSplitter import FOVMultiWellsSplitter
from eggcounting.split_fov.helper import was_fov_split, parse_camera_serial


def add_wells_to_hdf5(hdf5_fname, out_fname=None):
    """
    Apply FOV splitting algorithm to hdf5_fname.
    Writes output in dst_fname (which if empty will be the input file)

    Parameters
    ----------
    hdf5_fname : str or Path
        Input file.
        Needs to have a field named /full_data, with `microns_per_pixel`
        as a `_v_attrs`.
    out_fname : str or Path, optional
        Output file. The default is None. This makes output == input

    Returns
    -------
    None.

    """
    if out_fname is None:
        out_fname = hdf5_fname

    # split fov
    fovsplitter = FOVMultiWellsSplitter(
        hdf5_fname,
        total_n_wells=96,
        whichsideup='upright',
        well_shape='square',
        )
    # write output
    fovsplitter.write_fov_wells_to_file(out_fname)
    return


def assert_same_serial(annotations_fname, hdf5_fname):
    """
    Check annotations_fname and hdf5_fname pertain to the same camera

    Parameters
    ----------
    annotations_fname : str or Path
        path to annotations csv.
    hdf5_fname : str or Path
        path to hdf5.

    Returns
    -------
    None.

    """
    annotations_serial = parse_camera_serial(annotations_fname)
    hdf5_serial = parse_camera_serial(hdf5_fname)
    assert annotations_serial == hdf5_serial
    return


def _add_wells_to_annotations(
        annotations_fname, hdf5_fname=None,
        out_annotations_fname=None,
        out_hdf5_fname=None,
        ignore_old_well_names=False):
    """
    Assign well_names to each egg annotation by either reading /fov_wells from
    the hdf5 or using FOVsplitter on its first frame.

    Parameters
    ----------
    annotations_fname : str or Path
        path to annotations csv.
    hdf5_fname : str or Path, optional
        Input file.
        Needs a `/full_data` field, with `microns_per_pixel` as a `_v_attrs`
    out_annotations_fname : str or Path, optional
        Output file. The default is None. This makes output == input
    out_hdf5_fname : str or Path, optional
        Output hdf5 file. The default is None. This makes output == input
    ignore_old_well_names : Bool, optional
        If True, old well_names in eggs.csv will be ignored,
        and reassigned after FOV splitting the hdf5. The default is False.

    Returns
    -------
    None.

    """

    # input checks
    if isinstance(annotations_fname, str):
        annotations_fname = Path(annotations_fname)
    if hdf5_fname is None:
        hdf5_fname = Path(
            str(annotations_fname).replace('_eggs.csv', '.hdf5'))
        if not hdf5_fname.exists():
            print(
                ('Could not find an hdf5 file matching '
                 f'{annotations_fname}, skipping')
                )
            return

    if out_annotations_fname is None:
        out_annotations_fname = annotations_fname
    if out_hdf5_fname is None:
        out_hdf5_fname = hdf5_fname

    assert_same_serial(annotations_fname, hdf5_fname)

    # read wells
    annotations_df = pd.read_csv(annotations_fname)
    # check if this had already been done
    if 'well_name' in annotations_df.columns and not ignore_old_well_names:
        print(f'well_name already in {annotations_fname}, nothing to do here.')
        return

    # divide fov if not already done
    if not was_fov_split(hdf5_fname):
        add_wells_to_hdf5(hdf5_fname, out_fname=out_hdf5_fname)
    # read fov splitting info
    fovsplitter = FOVMultiWellsSplitter(hdf5_fname)

    # sort eggs into wells
    annotations_df['well_name'] = fovsplitter.find_well_of_xy(
        annotations_df['x'], annotations_df['y']).str.decode('utf-8')
    # write out
    annotations_df.to_csv(out_annotations_fname, index=False)

    return


def _add_wells_to_annotations_in_folder(
        data_dir, ignore_old_well_names=False):
    """
    Find matching hdf5 and eggs.csv annotation files in folder,
    then assign well_names to each of them by either reading /fov_wells from
    the matching hdf5 or using FOVsplitter on its first frame.

    Parameters
    ----------
    data_dir : str or Path
        path where to find the hdf5 and eggs.csv annotation files.
    ignore_old_well_names : Bool, optional
        If True, old well_names in eggs.csv will be ignored,
        and reassigned after FOV splitting the hdf5. The default is False.

    Returns
    -------
    None.

    """

    if isinstance(data_dir, str):
        data_dir = Path(data_dir)

    # find annotations
    annotations_fnames = list(data_dir.rglob('*_eggs.csv'))
    print(f'Found {len(annotations_fnames)} annotation files')

    # match with hdf5
    matching_anns_hdf5 = {}
    for ann_fname in annotations_fnames:
        tl_fname = Path(str(ann_fname).replace('_eggs.csv', '.hdf5'))
        if tl_fname.exists():
            matching_anns_hdf5[ann_fname] = tl_fname
    print(f'Found {len(list(matching_anns_hdf5.keys()))} matches')

    # loop over matched filenames, add wells
    for ann_fname, tl_fname in tqdm(matching_anns_hdf5.items()):
        _add_wells_to_annotations(
            ann_fname, tl_fname,
            ignore_old_well_names=ignore_old_well_names)

    return


def add_wells_to_annotations():
    fire.Fire(_add_wells_to_annotations)


def add_wells_to_annotations_in_folder():
    fire.Fire(_add_wells_to_annotations_in_folder)


if __name__ == '__main__':

    src_dir = Path('~/work_repos/EggCounting/data/unsplitted/').expanduser()
    hdf5_fname = 'r01_sp02_20201112_122940.22956822_timelapse.hdf5'
    anns_fname = 'r01_sp02_20201112_122940.22956822_timelapse_eggs.csv'

    dst_dir = Path('~/work_repos/EggCounting/data/splitted/').expanduser()

    from shutil import copy2
    copy2(src_dir / hdf5_fname, dst_dir)
    copy2(src_dir / anns_fname, dst_dir)

    _add_wells_to_annotations(
        dst_dir / anns_fname,
        dst_dir / hdf5_fname,
        ignore_old_well_names=False,
        )

    # _add_wells_to_annotations_in_folder('/Volumes/behavgenom$/Bonnie/Egg_laying_drug_screen/Timelapses/20201112')



