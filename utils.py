from os import path, remove, listdir

from random import choice
from string import ascii_uppercase, digits

import numpy as np

from skimage import draw, io, measure, color


def distance_between_points(x1, y1, x2, y2):
    return pow((x1 - x2)**2 + (y1 - y2)**2, 0.5)


def poly_area(coords_set):
    x = [x for x, y in coords_set]
    y = [y for x, y in coords_set]
    return 0.5*np.abs(np.dot(x, np.roll(y, 1))-np.dot(y, np.roll(x, 1)))


def img_to_black_white(img):
    tmp = np.zeros_like(color.rgba2rgb(img))
    tmp[img[:, :, 3] != 0] = 1
    return color.rgb2gray(tmp)


def biggest_contour(img):
    try:
        contours = measure.find_contours(img_to_black_white(img), 0.8)
    except ValueError:
        print("ValueError in biggest_contour. Probably the item is too little")
        return None

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
    # if red == green == blue:
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
            # temp_element.append(sk_element[0])
            # temp_element.append(sk_element[1])
            cv_element.append(temp_element)
            cv_contour.append(cv_element)
        cv_contours.append(np.asarray(cv_contour, dtype="float"))
    return cv_contours


def cut_img(img, min_x, max_x, min_y, max_y):
    return img[min_x:max_x, min_y:max_y]


def clear_directory(path_to_dir):
    for filename in listdir(path_to_dir):
        remove(path.join(path_to_dir, filename))


def skimage_split_to_items(img_path, green_img_path, output_path):
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


def generate_random_name(size=6, chars=ascii_uppercase + digits):
    return ''.join(choice(chars) for _ in range(size))
