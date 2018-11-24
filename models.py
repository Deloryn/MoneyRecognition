from enum import Enum

import numpy as np

from skimage import measure, io, exposure

from utils import distance_between_points, draw_contour, biggest_contour, biggest_region, calculate_distances_from_centroid, calculate_perimeter_from_contour, calculate_avg_color_int
from utils import calculate_avg_color_float


class DecisionTree:
    def __init__(self, items):
        self.items = items
        self.recognized = []
        self.unsure = []

    def solve(self):
        self.classify_items()
        self.classify_unsure_items()
        score = self.calculate_score()
        return score

    def classify_items(self):
        for item in self.items:
            result = item.classify()
            if result == Type.REJECTED:
                continue
            elif result == Type.UNSURE:
                self.unsure.append(item)
            else:
                self.recognized.append(item)

    def classify_unsure_items(self):
        recognized_unsures = []
        for unsure_item in self.unsure:
            for recognized_item in [x for x in self.recognized if x.value < 10]:
                result = recognized_item.compare_ratio(unsure_item)
                if result != Type.UNSURE:
                    unsure_item.value = result
                    recognized_unsures.append(unsure_item)
        self.recognized += recognized_unsures

    def calculate_score(self):
        score = 0
        for item in self.recognized:
            score += item.value
        return score


class Item:
    def __init__(self, img):
        self.img = img
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

    def is_rectangle(self):
        centroid = self.region.centroid
        distances_from_centroid = calculate_distances_from_centroid(self.contour, centroid)
        diagonal1 = 2 * max(distances_from_centroid)
        # diagonal2 = pow((0.5*self.region.perimeter)**2 -2*self.size, 0.5)
        perimeter = calculate_perimeter_from_contour(self.contour)
        diagonal2 = pow((0.5 * perimeter) ** 2 - 2 * self.size,
                        0.5)
        # print(diagonal1)
        # print(diagonal2)
        # print("")
        # if self.region.convex_area / self.size <= 1.2:
        if 1 <= diagonal2 / diagonal1 <= 1.2:
            return True
        else:
            return False
        # for x, y in self.contour:

        # min_x = min(x)
        # max_x = max(x)
        # min_y = min(y)
        # max_y = max(y)
        #
        # diagonal1 = distance_between_points(min_x, min_y, max_x, max_y)
        # diagonal2 = distance_between_points(max_x, min_y, min_x, max_y)
        #
        # if 0.8 <= diagonal2 / diagonal1 <= 1.2:
        #     rectangle_diagonal = pow((0.5 * self.region.perimeter)**2 - 2*self.region.area, 0.5)
        #     if (0.8 <= rectangle_diagonal/diagonal1 <= 1.2) or (0.8 <= rectangle_diagonal/diagonal2 <= 1.2):
        #         return True
        # return False

    def is_multishape(self):
        # TODO: implementacja. Moze byc trudne
        pass

    def classify(self):
        # TODO: na koncu ma byc self.value = konkretna wartosc
        # TODO: na koncu return Type.TYP
        if self.contour is None:
            self.value = 0
            return Type.REJECTED
        if self.is_circle():
            # self.value = 1
            # return Type.ONE_PLN
            self.value = 0
            return Type.REJECTED
        elif self.is_rectangle():
            avg_color = calculate_avg_color_float(self.img)
            red = avg_color[0]
            green = avg_color[1]
            blue = avg_color[2]
            #[0.355756461796403, 0.3897173477711009, 0.3882332225761498]

            copy = np.copy(self.img)
            copy = exposure.equalize_adapthist(copy)
            if (0.25 <= red <= 0.33) and abs(green-blue) <= 0.03: # banknot 20 zł
                self.value = 20
                return Type.TWENTY_PLN
            elif (0.33 <= red <= 0.45) and abs(green-blue) <= 0.03: # banknot 50 zl
                self.value = 50
                return Type.FIFTY_PLN
            else:
                # TODO: is multishape
                self.value = 0
                return Type.REJECTED
        # elif self.is_multishape():
        #     self.classify()
        else:
            self.value = 0
            return Type.REJECTED

    def compare_ratio(self, unsure_item):
        calculated_ratio = unsure_item.size / self.size
        if self.value == 0.20:
            ratio = {0.20: 1, 0.50: 1.108108, 1: 1.243243, 2: 1.162162, 5: 1.297297}
        elif self.value == 0.50:
            ratio = {0.20: 0.902439, 0.50: 1, 1: 1.121951, 2: 1.048780, 5: 1.170731}
        elif self.value == 1:
            ratio = {0.20: 0.804347, 0.50: 0.891304, 1: 1, 2: 0.934782, 5: 1.043478}
        elif self.value == 2:
            ratio = {0.20: 0.860465, 0.50: 0.953488, 1: 1.069767, 2: 1, 5: 1.116279}
        elif self.value == 5:
            ratio = {0.20: 0.770833, 0.50: 0.854166, 1: 0.958333, 2: 0.895833, 5: 1}
        else:
            return Type.UNSURE

        for key in ratio:
            ratio[key] = ratio[key]**2 # bo porownujemy pola obiektow
        epsilon = 0.05
        for key in ratio:
            if ratio[key]-epsilon <= calculated_ratio <= ratio[key]+epsilon:
                return key
        return Type.UNSURE


class Type(Enum):
    REJECTED = -1
    UNSURE = 0
    TWENTY_GROSS = 0.20
    FIFTY_GROSS = 0.50
    ONE_PLN = 1
    TWO_PLN = 2
    FIVE_PLN = 5
    TWENTY_PLN = 20
    FIFTY_PLN = 50
