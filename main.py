from os import listdir, path
from image_processing import mock_image_processing
from utils import skimage_split_to_items

BASE_DIR_PATH = path.dirname(path.abspath(__file__))
IMAGES_PATH = path.join(BASE_DIR_PATH, "images")
EASY_PATH = path.join(IMAGES_PATH, "easy")
MEDIUM_PATH = path.join(IMAGES_PATH, "medium")
HARD_PATH = path.join(IMAGES_PATH, "hard")

# Glowny program -------------------------------------------------
# easy_filenames = [path.join(EASY_PATH, f) for f in listdir(EASY_PATH) if path.isfile(path.join(EASY_PATH, f))]
# medium_filenames = [path.join(MEDIUM_PATH, f) for f in listdir(MEDIUM_PATH) if path.isfile(path.join(MEDIUM_PATH, f))]
# hard_filenames = [path.join(HARD_PATH, f) for f in listdir(HARD_PATH) if path.isfile(path.join(HARD_PATH, f))]

# all_filenames = easy_filenames + medium_filenames + hard_filenames
# for filename in all_filenames:
#     process_image(filename)
# ----------------------------------------------------------------


# MOCK --------------------------:
green_items_filenames = [path.join(BASE_DIR_PATH, "green", f) for f in listdir(path.join(BASE_DIR_PATH, "green"))]
medium_items_filenames = [path.join(MEDIUM_PATH, "items", f) for f in listdir(path.join(MEDIUM_PATH, "items"))]

mock_image_processing(green_items_filenames, medium_items_filenames)
# split_image_to_objects(medium_items_filenames[0], green_items_filenames[0], "objects")
# skimage_split_to_objects(medium_items_filenames[0], green_items_filenames[0], "objects")
# ------------------------------------------------------------
