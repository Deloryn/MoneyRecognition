from os import listdir, path, mkdir

import numpy as np

from skimage import measure
from skimage import io
from skimage import feature
from skimage import color
from skimage import img_as_uint, img_as_float
from skimage import draw
from skimage import morphology as mp
from skimage import filters

from utils import skimage_split_to_items, generate_random_name
from decision_tree import DecisionTree
from item import Item


import cv2


def mock_image_processing(green_filenames, medium_filenames):
    for i in range(len(green_filenames)):
        skimage_split_to_items(medium_filenames[i], green_filenames[i], "items")
        items_filenames = listdir("items")
        items_imgs = [io.imread(path.join("items", f)) for f in items_filenames]
        items = [Item(items_imgs[i]) for i in range(len(items_imgs))]

        decision_tree = DecisionTree(items)
        score = decision_tree.solve()

        output_path = path.join("output", medium_filenames[i][-5:])
        if not path.exists(output_path):
            mkdir(output_path)
        for j in range(len(items)):
            items[j].save_img(output_path+"/"+str(j)+"-value-"+str(items[j].value)+".png")

        print(medium_filenames[i] + ": " + str(score))
