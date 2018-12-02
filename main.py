from os import listdir, path
from solver import Solver

BASE_DIR_PATH = path.dirname(path.abspath(__file__))
IMAGES_PATH = path.join(BASE_DIR_PATH, "images")
EASY_PATH = path.join(IMAGES_PATH, "easy")
MEDIUM_PATH = path.join(IMAGES_PATH, "medium")
HARD_PATH = path.join(IMAGES_PATH, "hard")

easy_filenames = [path.join(EASY_PATH, f) for f in listdir(EASY_PATH) if path.isfile(path.join(EASY_PATH, f))]
# medium_filenames = [path.join(MEDIUM_PATH, f) for f in listdir(MEDIUM_PATH) if path.isfile(path.join(MEDIUM_PATH, f))]
# hard_filenames = [path.join(HARD_PATH, f) for f in listdir(HARD_PATH) if path.isfile(path.join(HARD_PATH, f))]
# all_filenames = easy_filenames + medium_filenames + hard_filenames

for filename in easy_filenames:
    solver = Solver(filename)
    total_value = solver.solve()
    print(filename + ": " + str(total_value))
