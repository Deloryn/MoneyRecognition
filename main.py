from os import listdir, path

import numpy as np

from skimage import measure
from skimage import io
from skimage import feature
from skimage import color
from skimage import img_as_uint

BASE_DIR_PATH = path.dirname(path.abspath(__file__))
IMAGES_PATH = path.join(BASE_DIR_PATH, "images")
EASY_PATH = path.join(IMAGES_PATH, "easy")
MEDIUM_PATH = path.join(IMAGES_PATH, "medium")
HARD_PATH = path.join(IMAGES_PATH, "hard")

easy_filenames = [path.join(EASY_PATH, f) for f in listdir(EASY_PATH) if path.isfile(path.join(EASY_PATH, f))]
medium_filenames = [path.join(MEDIUM_PATH, f) for f in listdir(MEDIUM_PATH) if path.isfile(path.join(MEDIUM_PATH, f))]
hard_filenames = [path.join(HARD_PATH, f) for f in listdir(HARD_PATH) if path.isfile(path.join(HARD_PATH, f))]

easy_imgs = [io.imread(f) for f in easy_filenames]
