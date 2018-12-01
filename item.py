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
        if max_distance / min_distance < 1.4:
            return True
        else:
            return False

    def is_multishape(self):
        # TODO: Ewa
        # if something:
        #     return True
        # else:
        #     return False
        pass

    def is_coin(self):
        copy = np.copy(self.img)
        red, green, blue = calculate_avg_color_float(copy)
        if abs(red-green) <= 34 and green-blue <= 30 and green > blue:
            h, s, v = calculate_avg_color_float(color.rgb2hsv(copy[:, :, :3]))
            if h <= 0.37 and s <= 0.44:
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
            if self.is_multishape():
                return Type.MULTISHAPE
            else:
                return Type.REJECTED
