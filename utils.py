import numpy as np

from skimage import draw, measure, color

from type import Type


def distance_between_points(x1, y1, x2, y2):
    return pow((x1 - x2)**2 + (y1 - y2)**2, 0.5)


def poly_area(coords_set):
    x = [x for x, y in coords_set]
    y = [y for x, y in coords_set]
    return 0.5*np.abs(np.dot(x, np.roll(y, 1))-np.dot(y, np.roll(x, 1)))


def is_coin(img):
    red, green, blue = calculate_avg_color(img)
    if abs(red-green) <= 34 and green-blue <= 30 and green > blue:
        h, s, v = calculate_avg_color(color.rgb2hsv(img[:, :, :3]))
        if h <= 0.37 and s <= 0.44:
            return True
    return False


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


def biggest_coords(img):
    mask = color.rgb2gray(img)
    mask[mask != 0] = 255
    all_coords = measure.find_contours(mask, 0.8)
    biggest_coords = None
    biggest_area = 0
    for coords in all_coords:
        area = poly_area(coords)
        if area > biggest_area:
            biggest_area = area
            biggest_coords = coords
    return biggest_coords


def biggest_region(img):
    mask = color.rgb2gray(img)
    mask[mask != 0] = 255
    mask[mask != 255] = 0
    regions = measure.regionprops(measure.label(mask))
    biggest_region = None
    biggest_area = 0
    for region in regions:
        area = region.area
        if area > biggest_area:
            biggest_region = region
            biggest_area = area
    return biggest_region


def calculate_distances_from_centroid(coords, centroid):
    distances_from_centroid = []
    for x, y in coords:
        distance = distance_between_points(x, y, centroid[0], centroid[1])
        distances_from_centroid.append(distance)
    return distances_from_centroid


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


def cut_img(img, min_x, max_x, min_y, max_y):
    return img[min_x:max_x, min_y:max_y]


def add_alpha(rgb):
    """Add an alpha layer to the image.

    The alpha layer is set to 1 for foreground
    and 0 for background.
    """
    rgba = []
    for element in rgb.tolist():
        new_element = []
        for pixel in element:
            new_pixel = pixel
            if new_pixel == [0, 0, 0]:
                new_pixel.append(0)
            else:
                new_pixel.append(255)
            new_element.append(new_pixel)
        rgba.append(new_element)
    return np.array(rgba)


def decide_if_two_or_five(item):
    outer = get_five_pln_outer_circle(item)
    outer_silverness = calculate_silverness(outer)
    if outer_silverness < 0.2:
        return 2
    else:
        return 5


def draw_contour(img, coords):
    r = [coord[0] for coord in coords]
    c = [coord[1] for coord in coords]
    rr, cc = draw.polygon_perimeter(r, c)
    img[rr, cc] = [0, 255, 0, 255]


def draw_shape(img, coords):
    r = [coord[0] for coord in coords]
    c = [coord[1] for coord in coords]
    rr, cc = draw.polygon(r, c)
    img[rr, cc] = 255
    return img


def draw_circle(img, circle, color):
    rr, cc = circle
    img[rr, cc] = color
    return img


def get_five_pln_outer_circle(item):
    outer = np.copy(item.img)
    centroid = item.region.centroid
    main_radius = item.contour.mean_distance
    radius = 0.7 * main_radius
    circle_contour = draw.circle(centroid[0], centroid[1], radius, shape=None)
    outer = draw_circle(outer, circle_contour, [0, 0, 0, 255])
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


def calculate_avg_color(img):
    red = np.mean(img[:, :, 0])
    green = np.mean(img[:, :, 1])
    blue = np.mean(img[:, :, 2])
    return red, green, blue


def calculate_goldness(img):
    gold_pixels = 0
    all_pixels = 0
    for element in img.tolist():
        for pixel in element:
            if pixel[0] != 0 and pixel[1] != 0 and pixel[2] != 0:
                all_pixels += 1
                if abs(pixel[0]-pixel[1]) + abs(pixel[1]-pixel[2]) > 25:
                    gold_pixels += 1
    if all_pixels == 0:
        return 0
    else:
        return gold_pixels/all_pixels


def calculate_silverness(img):
    silver_pixels = 0
    all_pixels = 0
    for element in img.tolist():
        for pixel in element:
            if pixel[0] != 0 and pixel[1] != 0 and pixel[2] != 0:
                all_pixels += 1
                if abs(pixel[0] - pixel[1]) + abs(pixel[1] - pixel[2]) <= 10:
                    silver_pixels += 1
    if all_pixels == 0:
        return 0
    else:
        return silver_pixels / all_pixels


def calculate_color_difference(img):
    differences = []
    for element in img.tolist():
        for pixel in element:
            rgb = pixel[:3]
            maxim = max(rgb)
            for color in rgb:
                differences.append(maxim-color)
    return sum(differences)


def is_multishape(img):
    # TODO: Ewa
    # if something then True
    # else False
    return False


def divide_multishape(img):
    # TODO: Ewa
    # return new_images, new_contours
    return [], []