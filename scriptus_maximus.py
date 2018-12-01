import skimage as ski
import skimage.morphology as mp
from skimage import io, filters
from skimage.color import rgb2gray
from scipy.ndimage import binary_fill_holes
import numpy as np
from PIL import Image
import sys
import os
from os import listdir, path


def binary_sobel(original, treshhold):
    res = np.zeros_like(original)
    
    grayscale_contour = filters.sobel(rgb2gray(original))
    
    grayscale_contour[(grayscale_contour > treshhold)] = 1
    grayscale_contour[(grayscale_contour < treshhold)] = 0
    
    return grayscale_contour


def get_contour_mask(original):
    is_table = original[:50].mean() < 56
    is_paper = original[:50].mean() > 170
    is_paper_on_carpet = original[-50:].mean() > 150
    
    res = np.copy(original)
    
    if is_table:
        img = rgb2gray(original)
        median_filter_range = 12
        binary_sobel_treshhold = 0.03
    elif is_paper:
        img = original[:,:,2]
        median_filter_range = 2
        binary_sobel_treshhold = 0.011
    else:
        img = original[:,:,1]
        median_filter_range = 10
        if is_paper_on_carpet:
            binary_sobel_treshhold = 0.011
        else:
            binary_sobel_treshhold = 0.024
    
    img = filters.median(img, mp.disk(median_filter_range))
    img = binary_sobel(img, binary_sobel_treshhold)
    
    if is_paper:
        img = mp.binary_dilation(img)
        img = mp.binary_dilation(img)
        
    img = binary_fill_holes(img)
    img = mp.binary_erosion(img)
    img = mp.binary_erosion(img)
    
    if not is_table and not is_paper and is_paper_on_carpet:
        img = mp.binary_erosion(img)
    
    img = mp.remove_small_objects(img, 2000)
        
    res[img == 1] = 255
    res[img == 0] = 0
    
    return res


def merge_images_vertically(imgs):
    images = [Image.fromarray(img) for img in imgs]

    widths, heights = zip(*(i.size for i in images))

    total_height = sum(heights)
    max_width = max(widths)

    new_im = Image.new('RGB', (max_width, total_height))

    y_offset = 0
    
    for im in images:
        new_im.paste(im, (0, y_offset))
        y_offset += im.size[1]

    return new_im
