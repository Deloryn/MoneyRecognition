from os import path, remove, listdir

from random import choice
from string import ascii_uppercase, digits

import numpy as np

from skimage import draw, io, measure, color
from skimage.filters import threshold_local
from skimage import filters


def distance_between_points(x1, y1, x2, y2):
    return pow((x1 - x2)**2 + (y1 - y2)**2, 0.5)


def poly_area(coords_set):
    x = [x for x, y in coords_set]
    y = [y for x, y in coords_set]
    return 0.5*np.abs(np.dot(x, np.roll(y, 1))-np.dot(y, np.roll(x, 1)))


def biggest_contour(img):
    # try:
    contours = measure.find_contours(img_to_black_white(img), 0.8)
    # except ValueError:
    #     print("ValueError in biggest_contour. Probably the item is too little")
    # return None

    biggest_contour = None
    biggest_area = 0
    for contour in contours:
        area = poly_area(contour)
        if area > biggest_area:
            biggest_area = area
            biggest_contour = contour
    return biggest_contour


def biggest_region(img):
    regions = measure.regionprops(measure.label(img))
    biggest_region = None
    biggest_area = 0
    for region in regions:
        area = region.area
        if area > biggest_area:
            biggest_region = region
            biggest_area = area
    return biggest_region


def calculate_distances_from_centroid(contour, centroid):
    distances_from_centroid = []
    for x, y in contour:
        distance = distance_between_points(x, y, centroid[0], centroid[1])
        distances_from_centroid.append(distance)
    return distances_from_centroid


def calculate_perimeter_from_contour(contour):
    perimeter = 0
    vertices = contour.tolist()
    for i in range(len(vertices)-1):
        x1 = vertices[i][0]
        y1 = vertices[i][1]

        x2 = vertices[i+1][0]
        y2 = vertices[i+1][1]

        perimeter += distance_between_points(x1, y1, x2, y2)
    return perimeter


def get_closest_key_from_ratio(ratio, item_ratio):
    diffs = []
    keys = []
    for key in ratio:
        keys.append(key)
        diffs.append(abs(item_ratio - ratio[key]))
    return keys[[i for i in range(len(diffs)) if diffs[i] == min(diffs)][0]]


def sk2cv_contours(sk_contours):
    cv_contours = []
    for sk_contour in sk_contours:
        sk_contour = sk_contour.tolist()
        cv_contour = []
        for sk_element in sk_contour:
            cv_element = []
            temp_element = []
            temp_element.append(int(round(sk_element[0])))
            temp_element.append(int(round(sk_element[1])))
            cv_element.append(temp_element)
            cv_contour.append(cv_element)
        cv_contours.append(np.asarray(cv_contour, dtype="float"))
    return cv_contours


def clear_directory(path_to_dir):
    for filename in listdir(path_to_dir):
        remove(path.join(path_to_dir, filename))


def generate_random_name(size=6, chars=ascii_uppercase + digits):
    return ''.join(choice(chars) for _ in range(size))


def cut_img(img, min_x, max_x, min_y, max_y):
    return img[min_x:max_x, min_y:max_y]


def threshold_img(img, blocksize=111):
    copy = np.copy(img)
    copy = filters.gaussian(copy)
    gray = color.rgb2gray(copy)
    thresh = threshold_local(gray, blocksize)
    binary = gray > thresh
    copy[binary != 1] = [0, 0, 0, 255]
    copy = filters.sobel(color.rgb2gray(copy))
    return copy


def img_to_black_white(img):
    tmp = np.zeros_like(color.rgba2rgb(img))
    tmp[img[:, :, 3] != 0] = 1
    return color.rgb2gray(tmp)


def skimage_split_to_items_from_path(img_path, green_img_path, output_path):
    clear_directory(output_path)
    base_img = io.imread(img_path)
    green_img = io.imread(green_img_path)

    contours = measure.find_contours(color.rgb2gray(green_img), 0.8)
    for i in range(len(contours)):
        mask = np.zeros_like(base_img)
        mask = draw_shape(color.rgb2gray(mask), contours[i])
        out = np.zeros_like(base_img)
        out[mask == 255] = base_img[mask == 255]
        x = [x for x, y in contours[i]]
        y = [y for x, y in contours[i]]
        out = cut_img(out, int(min(x)), int(max(x))+2, int(min(y)), int(max(y))+2)
        io.imsave(path.join(output_path, "item"+str(i)+".png"), out)


def skimage_split_to_items_from_arrays(image, mask, output_path):
    clear_directory(output_path)
    base_img = image
    green_img = mask

    contours = measure.find_contours(color.rgb2gray(green_img), 0.8)
    for i in range(len(contours)):
        mask = np.zeros_like(base_img)
        mask = draw_shape(color.rgb2gray(mask), contours[i])
        out = np.zeros_like(base_img)
        out[mask == 255] = base_img[mask == 255]
        out[color.rgb2gray(out) == 0] = [0, 0, 0]
        out = add_alpha(out)
        x = [x for x, y in contours[i]]
        y = [y for x, y in contours[i]]
        out = cut_img(out, int(min(x)), int(max(x))+2, int(min(y)), int(max(y))+2)
        io.imsave(path.join(output_path, "item"+str(i)+".png"), out)


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
    outer_part = get_outer_five_pln_circle(item.img, item.contour, item.region.centroid)
    inner_part = get_inner_five_pln_circle(item.img, item.contour, item.region.centroid)

    outer_goldness = calculate_goldness(outer_part)
    inner_goldness = calculate_goldness(inner_part)

    outer_silverness = calculate_silverness(outer_part)
    inner_silverness = calculate_silverness(inner_part)

    if outer_goldness > 0.5:
        return 2
    else:
        return 5


def draw_contour(img, contour):
    r = [coords[0] for coords in contour]
    c = [coords[1] for coords in contour]
    rr, cc = draw.polygon_perimeter(r, c)
    img[rr, cc] = [0, 255, 0, 255]


def draw_shape(img, contour):
    r = [coords[0] for coords in contour]
    c = [coords[1] for coords in contour]
    rr, cc = draw.polygon(r, c)
    img[rr, cc] = 255
    return img


def draw_circle(img, circle, color=[0, 255, 0, 255]):
    rr, cc = circle
    img[rr, cc] = color


def get_outer_five_pln_circle(img, contour, centroid):
    copy = np.copy(img)
    main_radius = np.mean(np.array(calculate_distances_from_centroid(contour, centroid)))
    radius = 0.7 * main_radius
    circle_contour = draw.circle(centroid[0], centroid[1], radius, shape=None)
    draw_circle(copy, circle_contour, [0, 0, 0, 255])
    return copy


def get_inner_five_pln_circle(img, contour, centroid):
    outer_img = get_outer_five_pln_circle(img, contour, centroid)
    inner_img = np.zeros_like(outer_img)
    inner_img[color.rgb2gray(outer_img) == 0] = img[color.rgb2gray(outer_img) == 0]
    return inner_img


def flatten_img_array(img):
    pixels = []
    for element in img.tolist():
        for pixel in element:
            if pixel[0] != 0 and pixel[1] != 0 and pixel[2] != 0:
                pixels.append(pixel[:3])
    return pixels


def calculate_avg_color_int(img):
    red = 0
    green = 0
    blue = 0
    count = 0
    img_list = img.tolist()
    for element in img_list:
        for pixel in element:
            count += 1
            red += pixel[0]
            green += pixel[1]
            blue += pixel[2]
    red //= count
    green //= count
    blue //= count
    return red, green, blue


def calculate_avg_color_float(img):
    red = 0
    green = 0
    blue = 0
    count = 0
    img_list = img.tolist()
    for element in img_list:
        for pixel in element:
            count += 1
            red += pixel[0]
            green += pixel[1]
            blue += pixel[2]
    red /= count
    green /= count
    blue /= count
    return red, green, blue


def is_pixel_silver(pixel):
    red = pixel[0]
    green = pixel[1]
    blue = pixel[2]
    if abs(red - green) <= 10 and abs(red - green) <= 15:
        return True
    else:
        return False


def calculate_silver_percentage(img):
    img_list = img.tolist()
    silver_count = 0
    all_count = 0
    for element in img_list:
        for pixel in element:
            all_count += 1
            if is_pixel_silver(pixel):
                silver_count += 1
    print("Silver count: " + str(silver_count))
    print("All count: " + str(all_count))
    print(silver_count / all_count)
    print("")
    print("")
    return silver_count / all_count


def calculate_goldness(img):
    gold_pixels = 0
    all_pixels = 0
    for element in img.tolist():
        for pixel in element:
            if pixel[0] != 0 and pixel[1] != 0 and pixel[2] != 0:
                all_pixels += 1
                if abs(pixel[0]-pixel[1]) + abs(pixel[1]-pixel[2]) > 25:
                    gold_pixels += 1
    return gold_pixels/all_pixels


def calculate_silverness(img):
    silver_pixels = 0
    all_pixels = 0
    for element in img.tolist():
        for pixel in element:
            if pixel[0] != 0 and pixel[1] != 0 and pixel[2] != 0:
                all_pixels += 1
                if abs(pixel[0] - pixel[1]) + abs(pixel[1] - pixel[2]) < 10:
                    silver_pixels += 1
    return silver_pixels / all_pixels


def is_pixel_grayscale(pixel):
    red = pixel[0]
    green = pixel[1]
    blue = pixel[2]
    if abs(red - green) <= 10 and abs(red - green) <= 10:
        # if red == green == blue:
        return True
    else:
        return False


def calculate_color_difference(img):
    differences = []
    for element in img.tolist():
        for pixel in element:
            rgb = pixel[:3]
            maxim = max(rgb)
            for color in rgb:
                differences.append(maxim-color)
    return sum(differences)


def mean_color_without_black(img, color=""):
    red = 0
    green = 0
    blue = 0
    count = 0
    for element in img.tolist():
        for pixel in element:
            if pixel[0] != 0 and pixel[1] != 0 and pixel[2] != 0:
                count += 1
                red += pixel[0]
                green += pixel[1]
                blue += pixel[2]
    if color == "r":
        return red/count
    elif color == "g":
        return green/count
    elif color == "b":
        return blue/count
    else:
        return (red+green+blue)/3/count
