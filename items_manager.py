import numpy as np

from skimage import measure, color

from utils import is_multishape, divide_multishape, is_coin, check_monochromaticity, biggest_region, remove_border_from_circle, calculate_color_difference, draw_shape, cut_img, add_alpha

from contour_mask import get_contour_mask

from item import Item

from contour import Contour

from constants import Constants

from type import Type


class ItemsManager:
    constants = None

    def __init__(self, origin_img):
        items_imgs, contours = self.__origin_img_to_items_imgs(origin_img)
        self.items = ItemsManager.__create_items(items_imgs, contours)

    @staticmethod
    def __origin_img_to_items_imgs(origin_img):
        mask = get_contour_mask(origin_img)

        contours = measure.find_contours(color.rgb2gray(mask), 0.8)
        items_imgs = []
        for i in range(len(contours)):
            mask = np.zeros_like(origin_img)
            mask = draw_shape(color.rgb2gray(mask), contours[i])
            item_img = np.zeros_like(origin_img)
            item_img[mask == 255] = origin_img[mask == 255]
            item_img[color.rgb2gray(item_img) == 0] = [0, 0, 0]
            item_img = add_alpha(item_img)
            x = [x for x, y in contours[i]]
            y = [y for x, y in contours[i]]
            item_img = cut_img(item_img, int(min(x)), int(max(x)) + 2, int(min(y)),
                          int(max(y)) + 2)
            items_imgs.append(item_img)
        return items_imgs, contours

    @staticmethod
    def __create_items(items_imgs, contours):
        regions = []
        circles = []
        coins = []
        color_amplitudes = []
        no_of_coins = 0
        areas = []
        coins_color_diffs_percentages = []
        contour_objects = []
        for i, img in enumerate(items_imgs):
            if is_multishape(img):
                print("jest multishape")
                new_images, new_contours = divide_multishape(img)
                items_imgs[i] = None
                contours[i] = None
                items_imgs = items_imgs[:i] + items_imgs[i+1:] + new_images
                contours = contours[:i] + contours[i+1:] + new_contours

            contour = contours[i]
            if contour is None:
                print("contour jest None")
                items_imgs[i] = None
                continue

            contour_object = Contour(contour)
            region = biggest_region(img)
            if region is None:
                print("region jest None")
                items_imgs[i] = None
                continue

            area = region.area
            if area <= 5:
                print("area: " + str(area))
                print("area <= 5")
                items_imgs[i] = None
                continue

            areas.append(area)
            circle = False
            coin = False
            if contour_object.is_circle():
                circle = True
                # img = remove_border_from_circle(img, contour, region.centroid)
                if is_coin(img):
                    coin = True
                    no_of_coins += 1
                    avg_red = np.mean(img[:, :, 0])
                    avg_green = np.mean(img[:, :, 1])
                    avg_blue = np.mean(img[:, :, 2])
                    avg_color = np.mean(img[:, :, :3])
                    diffs = abs(avg_red - avg_green) + abs(avg_green - avg_blue)
                    percentage = diffs / avg_color
                    coins_color_diffs_percentages.append(percentage)
                    amplitude = calculate_color_difference(img)
                    color_amplitudes.append(amplitude)
                else:
                    color_amplitudes.append(0)
            regions.append(region)
            circles.append(circle)
            coins.append(coin)
            contour_objects.append(contour_object)

        parameter = 0
        if no_of_coins > 0:
            mean_color_amplitude = sum(color_amplitudes) / no_of_coins
            diff_from_mean = sum(([abs(mean_color_amplitude - x) for x in color_amplitudes if x != 0]))
            parameter = diff_from_mean / mean_color_amplitude / no_of_coins
        else:
            mean_color_amplitude = 0

        all_mono_or_not_mono = False
        if parameter < 0.2:
            mean_color_amplitude = 0
            color_amplitudes = [0] * len(color_amplitudes)
            all_mono_or_not_mono = True

        items = []
        mono_items = []
        not_mono_items = []
        mono_or_not_mono_items = []
        if len(color_amplitudes) != len(items_imgs):
            color_amplitudes += ([0] * (len(items_imgs) - len(color_amplitudes)))

        if regions and circles and coins and contour_objects:
            for i in range(len(items_imgs)):
                img = items_imgs[i]
                if img is not None:
                    if coins[i] == True:
                        monochromaticity = check_monochromaticity(color_amplitudes[i], mean_color_amplitude)
                    else:
                        monochromaticity = Type.UNSURE
                    item = Item(img, contour_objects[i], regions[i], circles[i], coins[i], monochromaticity)
                    items.append(item)
                    if monochromaticity == Type.MONOCHROMATIC_COIN:
                        mono_items.append(item)
                    elif monochromaticity == Type.NOT_MONOCHROMATIC_COIN:
                        not_mono_items.append(item)
                    elif monochromaticity == Type.ALL_MONO_OR_ALL_NOT_MONO:
                        mono_or_not_mono_items.append(item)
        ItemsManager.constants = Constants(areas,
                                           mean_color_amplitude,
                                           coins_color_diffs_percentages,
                                           all_mono_or_not_mono,
                                           mono_items,
                                           not_mono_items,
                                           mono_or_not_mono_items)
        return items
