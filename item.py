from os import path
from skimage import io


class Item:
    def __init__(self, img, contour, region, is_circle, is_coin, monochromaticity):
        self.img = img
        self.contour = contour
        self.region = region
        self.is_circle = is_circle
        self.is_coin = is_coin
        self.monochromaticity = monochromaticity
        self.value = 0

    def save_img(self, output_dir, filenumber):
        filename = str(filenumber) + "-value-" + str(self.value) + ".png"
        full_path = path.join(output_dir, filename)
        io.imsave(full_path, self.img)
