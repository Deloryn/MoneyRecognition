import numpy as np
from scipy import ndimage as ndi
from skimage import measure, color

from constants import Constants
from contour_mask import get_contour_mask
from split_objects import get_splitted_objects_labels
from type import Type
from utils import check_monochromaticity, props_describe_circle, props_describe_coin, calculate_color_diff, \
    calculate_avg_rgb, calculate_avg_hsv


class ItemsManager:
    constants = None

    def __init__(self, origin_img):
        self.region_props = self.__get_region_props(self, origin_img)
        self.__prepare_items(self, self.region_props)

    @staticmethod
    def __prepare_items(self, region_props):

        no_of_coins = 0

        for props in region_props:

            img = props.color_image

            if props.area <= 5:
                props.coin = False
                props.value = 0
                # region_props.remove(props)
                continue

            props.circle = False
            props.coin = False
            props.value = 0

            if props_describe_circle(props):
                props.circle = True

                calculate_avg_rgb(props)
                calculate_avg_hsv(props)

                if props_describe_coin(props):
                    props.coin = True
                    no_of_coins += 1

                    avg_color = props.mean_intensity

                    diffs = abs(props.avg_red - props.avg_green) + abs(props.avg_green - props.avg_blue)
                    props.diff_percentage = diffs / avg_color
                    props.amplitude = calculate_color_diff(img)
                else:
                    props.amplitude = 0
            else:
                if not props.after_split:
                    labels, num_features = get_splitted_objects_labels(img)

                    if num_features > 1:
                        new_region_props = self.__get_region_props_from_labels(labels, True, img)
                        region_props += new_region_props


        parameter = 0
        if no_of_coins > 0:
            color_amplitudes = np.array([props.amplitude for props in region_props if props.coin])
            mean_color_amplitude = sum(color_amplitudes) / no_of_coins
            diff_from_mean = sum(([abs(mean_color_amplitude - x) for x in color_amplitudes if x != 0]))
            parameter = diff_from_mean / mean_color_amplitude / no_of_coins
        else:
            mean_color_amplitude = 0

        all_mono_or_not_mono = False
        if parameter < 0.175:
            mean_color_amplitude = 0
            for props in region_props:
                props.amplitude = 0
            all_mono_or_not_mono = True

        mono_items = []
        not_mono_items = []
        mono_or_not_mono_items = []

        for props in region_props:
            if props.coin:
                props.monochromaticity = check_monochromaticity(props.amplitude, mean_color_amplitude)
            else:
                props.monochromaticity = Type.UNSURE

            if props.monochromaticity == Type.MONOCHROMATIC_COIN:
                mono_items.append(props)
            elif props.monochromaticity == Type.NOT_MONOCHROMATIC_COIN:
                not_mono_items.append(props)
            elif props.monochromaticity == Type.ALL_MONO_OR_ALL_NOT_MONO:
                mono_or_not_mono_items.append(props)

        mean_h = np.mean([props.avg_h for props in region_props if props.coin])
        mean_s = np.mean([props.avg_s for props in region_props if props.coin])
        mean_v = np.mean([props.avg_v for props in region_props if props.coin])

        areas = [props.area for props in region_props]
        coins_color_diffs_percentages = [props.diff_percentage for props in region_props if props.coin]

        ItemsManager.constants = Constants(areas,
                                           mean_color_amplitude,
                                           coins_color_diffs_percentages,
                                           all_mono_or_not_mono,
                                           mono_items,
                                           not_mono_items,
                                           mono_or_not_mono_items,
                                           mean_h,
                                           mean_s,
                                           mean_v)

    @staticmethod
    def __get_region_props(self, origin_img):

        mask = get_contour_mask(origin_img)
        labels, num_features = ndi.label(mask)
        return self.__get_region_props_from_labels(labels, False, origin_img)

    @staticmethod
    def __get_region_props_from_labels(labels, after_split, origin_img):
        region_props_3dim = measure.regionprops(labels, origin_img)
        labels_2dim = labels[:, :, 0]
        img_2img = (color.rgb2gray(origin_img) * 255).astype(int)
        region_props_2dim = measure.regionprops(labels_2dim, img_2img)
        for i in range(len(region_props_2dim)):
            region_props_2dim[i].color_image = region_props_3dim[i].intensity_image
            region_props_2dim[i].after_split = after_split

        return region_props_2dim
