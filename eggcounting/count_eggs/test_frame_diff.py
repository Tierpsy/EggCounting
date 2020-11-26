#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 10:01:24 2017

@author: ajaver
"""
import numpy as np
import tables
import matplotlib.pylab as plt
from scipy.ndimage.filters import median_filter

fname = '/Users/ajaver/OneDrive - Imperial College London/optogenetics/ATR_210417/A10_B0_1.5x_25fps_Ch1_21042017_163235.hdf5'

with tables.File(fname, 'r') as fid:
    full_frames = fid.get_node('/full_data')[:]

Id = (full_frames[-1] - full_frames[0].astype(np.float))/full_frames[0]
#%%
Id_n = Id*-1
Id_n[Id_n<0] = 0
plt.imshow(Id_n)

#%%
img = full_frames[-1]

th = 0.1
patch_neg = Id>-th

patch_neg = median_filter(patch_neg, (3,3))


top = img.max()
bot = img.min()
img_n = (img-bot)/(top-bot) 
img_rgb = np.repeat(img_n[..., None], 3, axis=2)
#img_rgb = img_rgb.astype(np.uint8)
img_rgb[...,0] = ((patch_neg) - 0.5)*img_rgb[...,0]

#%%
plt.imshow(img_rgb)


