from utils import *

from type import Type


class Item:
    def __init__(self, img):
        self.img = img
        self.color_diff = 0
        self.color_diff_border = 0
        self.circle = False
        self.coin = False
        self.contour = biggest_contour(img)
        if self.contour is not None:
            self.region = biggest_region(img)
            self.size = self.region.area
            if self.size <= 20:
                self.contour = None
                self.region = None
                self.size = 0
        else:
            self.region = None
            self.size = 0
        self.value = 0

    def save_img(self, path):
        io.imsave(path, self.img)

    def is_circle(self):
        centroid = self.region.centroid
        distances_from_centroid = calculate_distances_from_centroid(self.contour, centroid)
        min_distance = min(distances_from_centroid)
        max_distance = max(distances_from_centroid)
        if max_distance / min_distance < 1.20:
            return True
        else:
            return False

    def is_multishape(self):
        # TODO: implementacja. Moze byc trudne
        pass

    def is_coin(self):
        copy = np.copy(self.img)
        red, green, blue = calculate_avg_color_float(copy)
        if red-green <= 25 and blue-green <= 30 and red >= 50:
            h, s, v = calculate_avg_color_float(color.rgb2hsv(copy[:, :, :3]))
            if h <= 0.13 and s <= 0.44:
                return True
        return False

    def is_monochromatic(self):
        if self.color_diff != 0 and self.color_diff_border != 0 and self.color_diff <= self.color_diff_border:
            return True
        else:
            return False

    def classify(self):
        if self.contour is None:
            return Type.REJECTED
        if self.circle:
            if self.coin:
                if self.is_monochromatic():
                    return Type.MONOCHROMATIC_COIN
                else:
                    if self.color_diff_border == 0 and self.color_diff == 0:
                        return Type.ALL_MONO_OR_ALL_NOT_MONO
                    else:
                        return Type.NOT_MONOCHROMATIC_COIN
            else:
                return Type.REJECTED
        else:
            return Type.REJECTED


# elif self.value == 2:
#     ratio = {0.20: 0.860465, 0.50: 0.953488, 1: 1.069767, 2: 1, 5: 1.116279}
# elif self.value == 5:
#     ratio = {0.20: 0.770833, 0.50: 0.854166, 1: 0.958333, 2: 0.895833, 5: 1}