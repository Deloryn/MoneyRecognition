from os import listdir, path

import numpy as np

from skimage import measure
from skimage import io
from skimage import feature
from skimage import color
from skimage import img_as_uint

BASE_PATH = path.dirname(path.abspath("__file__"))

easy_filenames = [path.join("images/easy", f) for f in listdir("images/easy") if path.isfile(path.join("images/easy", f))]
# med_easy_filenames = [path.join("images/medium_easy", f) for f in listdir("images/medium_easy") if path.isfile(path.join("images/medium_easy", f))]
# med_hard_filenames = [path.join("images/medium_hard", f) for f in listdir("images/medium_hard") if path.isfile(path.join("images/medium_hard", f))]
# hard_filenames = [path.join("images/hard", f) for f in listdir("images/hard") if path.isfile(path.join("images/hard", f))]

easy_imgs = [io.imread(f) for f in easy_filenames]
