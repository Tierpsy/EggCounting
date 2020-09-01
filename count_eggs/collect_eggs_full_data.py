#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 13:53:05 2019

@author: lferiani

use in a tierpsy environment maybe?

"""
import cv2
import tqdm
import h5py
import shutil
import pandas as pd
from pathlib import Path
from multiprocessing import Pool



def find_all_data(path):
    """find all eggs files and associated hdf5 file, returns a dict eggs<=>masked"""
    
    # constants
    eggs_string = '_eggs.csv'
    masked_string = '.hdf5'
    
    # find all eggs
    eggs = list(path.rglob('*_eggs.csv'))
    
    # match eggs to hdf5
    masked = [Path(str(egg).replace(eggs_string, masked_string)) for egg in eggs]
    
    # chuck into dataframe
    egg2masked = pd.DataFrame.from_dict({'Eggs':eggs, 'MaskedVideos':masked})
    
    # drop non existing
    idx_good_rows = egg2masked['MaskedVideos'].apply(Path.exists)
    egg2masked.drop(egg2masked[~idx_good_rows].index, inplace=True)
    
    
    print('{} egg files found'.format(len(eggs)))
    print('{} egg <=> masked videos matches found'.format(len(egg2masked)))
    
    return egg2masked
    

def extract_from_one(_egg2masked_row, _source, _dest):
    """Needs egg, masked name, extracts full_data frames that are needed.
    Returns a dictionary with savename of the images, and images"""
    
    _egg = _egg2masked_row['Eggs']
    _masked = _egg2masked_row['MaskedVideos']
    
    # read eggs csv
    egg_df = pd.read_csv(_egg)
    
    # save frames that appear in the csv
    with h5py.File(_masked,'r') as fid:
        # create dest folder
        _img_parent = Path(str(_masked.parent).replace(str(_source),str(_dest)))
        if not _img_parent.exists():
                _img_parent.mkdir(parents=True, exist_ok=True)
        for frame_number in egg_df['frame_number'].unique():
            _img_name = _img_parent / _masked.name.replace('.hdf5','_frame-{:d}.png'.format(frame_number))
            _img = fid['full_data'][frame_number]
#            _img_dict[_img_name]=_img
            
            # save image
#            print(_img.shape )
#            print('saving to {}'.format(_img_name))
            cv2.imwrite(str(_img_name), _img)
    
    # and also copy the egg file
#    print()
    _egg_dest = str(_egg).replace(str(_source),str(_dest))
    shutil.copy2(_egg, _egg_dest)

    
    return 
   


#%%
if __name__=='__main__':
    
    source_dir = Path('/Volumes/behavgenom_archive$/Adam/screening/Syngenta/MaskedVideos/data/')
#    source_dir = Path('/Volumes/behavgenom$/Adam/Screening/Syngenta_multi_dose_three_replicates/MaskedVideos/')
    dest_dir = Path.home() / 'OneDrive - Imperial College London/out/Adam_egg_data_for_Avelino'
    
    
    # get eggs <=> masked video 
    annotation_df = find_all_data(source_dir)
    all_annotations =[x for _, x in annotation_df.iterrows()]
    
    # helpre function that only takes one input. uses Python weird scope permeability
    def _process_egg(row):
        return extract_from_one(row, source_dir, dest_dir)
    
    
    # one thread only for debugging
#    for row in all_annotations:
#        _process_egg(row)
    
    # else use this
    batch_size=8;
    
    for ind in tqdm.tqdm(range(0, len(all_annotations), batch_size)):
        
#        print(ind)
        rows = all_annotations[ind:ind+batch_size]
    
        with Pool(batch_size) as p:
                outs = p.imap_unordered(_process_egg, rows)
                for _ in outs:
                    pass
    
