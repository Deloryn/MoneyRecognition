import os

import numpy as np

from skimage import measure
from skimage import io
from skimage import feature
from skimage import color
from skimage import img_as_uint


BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def process(path):
    img = io.imread(path, as_gray=True)
    processed_img = feature.canny(img, sigma=0.8)
    io.imsave(os.path.join(BASE_PATH, "processed_images", "processed.jpg"), processed_img)
    return processed_img


for filename in os.listdir("images"):
    process(os.path.join(BASE_PATH, "images", filename))
