import numpy as np
from skimage import draw, color

from type import Type


def check_monochromaticity(color_amplitude, mean_color_amplitude):
    if color_amplitude != 0 and mean_color_amplitude != 0 and color_amplitude <= mean_color_amplitude:
        print("mono")
        return Type.MONOCHROMATIC_COIN
    else:
        if color_amplitude == 0 and mean_color_amplitude == 0:
            print("all mono or not mono")
            return Type.ALL_MONO_OR_ALL_NOT_MONO
        else:
            print("not mono")
            return Type.NOT_MONOCHROMATIC_COIN


def get_closest_key_from_ratio(ratio, item_ratio):
    diffs = []
    keys = []
    for key in ratio:
        keys.append(key)
        diffs.append(abs(item_ratio - ratio[key]))
    chosen_indexes = [i for i in range(len(diffs)) if diffs[i] == min(diffs)]
    chosen_keys = [keys[i] for i in chosen_indexes]
    if len(chosen_keys) == 1:
        return chosen_keys[0]
    else:
        return max(chosen_keys)


def decide_if_two_or_five(props):
    outer = get_five_pln_outer_circle(props)
    outer_silverness = calculate_silverness(outer)
    if outer_silverness < 0.2:
        return 2
    else:
        return 5


def draw_circle(img, circle, color):
    rr, cc = circle
    img[rr, cc] = color
    return img


def get_five_pln_outer_circle(props):
    outer = np.copy(props.color_image)
    main_radius = props.equivalent_diameter / 2
    radius = 0.7 * main_radius
    circle_contour = draw.circle(props.local_centroid[0], props.local_centroid[1], radius, shape=None)
    outer = draw_circle(outer, circle_contour, [0, 0, 0])
    return outer


def get_coin_middle(item):
    copy = np.copy(item.img)
    centroid = item.region.centroid
    main_radius = item.contour.mean_distance
    radius = 0.69 * main_radius
    circle_contour = draw.circle(centroid[0], centroid[1], radius, shape=None)
    copy = draw_circle(copy, circle_contour, [0, 0, 0, 255])
    gray_copy = color.rgb2gray(copy)
    print(gray_copy.tolist())
    coin_middle = np.zeros_like(item.img)
    coin_middle[gray_copy == 0] = item.img[gray_copy == 0]
    return coin_middle


def calculate_mean_middle_goldness(items):
    goldness = []
    for item in items:
        img = get_coin_middle(item)
        goldness.append(calculate_goldness(img))
    if goldness:
        return sum(goldness) / len(goldness)
    else:
        return 0


def remove_border_from_circle(item):
    copy = np.copy(item.img)
    centroid = item.region.centroid
    main_radius = item.contour.mean_distance
    radius = 0.95 * main_radius
    circle_contour = draw.circle(centroid[0], centroid[1], radius, shape=None)
    try:
        copy = draw_circle(copy, circle_contour, [0, 0, 0, 255])
    except IndexError:
        # circle wychodzi poza ramy obrazka?
        return

    out = np.zeros_like(copy)
    gray = color.rgb2gray(copy)
    out[gray == 0] = item.img[gray == 0]
    item.img = out


def calculate_goldness(img):
    img = img.astype(int)

    pixels_vector = np.logical_and(np.logical_and(img[:, :, 0] != 0, img[:, :, 1] != 0), img[:, :, 2] != 0)
    all_pixels = np.sum(pixels_vector)

    gold_candidates = np.abs(img[:,:,0] - img[:,:,1]) + np.abs(img[:,:,1] - img[:,:,2])
    gold_pixels = np.sum(np.logical_and(pixels_vector, gold_candidates > 25))

    return gold_pixels / all_pixels


def calculate_silverness(img):
    img = img.astype(int)

    pixels_vector = np.logical_and(np.logical_and(img[:, :, 0] != 0, img[:, :, 1] != 0), img[:, :, 2] != 0)
    all_pixels = np.sum(pixels_vector)

    silver_candidates = np.abs(img[:, :, 0] - img[:, :, 1]) + np.abs(img[:, :, 1] - img[:, :, 2])
    silver_pixels = np.sum(np.logical_and(pixels_vector, silver_candidates <= 10))
    return silver_pixels / all_pixels


def calculate_color_diff(img):
    hsv_img = (color.rgb2hsv(img) * 255).astype(int)
    img = img.astype(int)
    return np.sum(3 * hsv_img[:, :, 2] - (img[:, :, 0] + img[:, :, 1] + img[:, :, 2]))


def props_describe_circle(props):
    return props.eccentricity < 0.60


def props_describe_coin(props):
    if abs(props.avg_red - props.avg_green) <= 34 and \
            props.avg_green - props.avg_blue <= 30 and \
            props.avg_green > props.avg_blue:

        if props.avg_h <= 0.37 and props.avg_s <= 0.44:
            return True

    return False


def calculate_avg_hsv(props):
    area = props.bbox_area
    img = props.color_image

    hsv_img = color.rgb2hsv(img)
    props.avg_h = np.sum(hsv_img[:, :, 0]) / area
    props.avg_s = np.sum(hsv_img[:, :, 1]) / area
    props.avg_v = np.sum(hsv_img[:, :, 2]) / area


def calculate_avg_rgb(props):
    area = props.bbox_area
    img = props.color_image

    props.avg_red = np.sum(img[:, :, 0]) / area
    props.avg_green = np.sum(img[:, :, 1]) / area
    props.avg_blue = np.sum(img[:, :, 2]) / area
