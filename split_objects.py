from scipy import ndimage as ndi
import numpy as np
from skimage.morphology import watershed


def get_splitted_objects_labels(image):
    dist = ndi.distance_transform_edt(image)

    threshold = 0
    coins = 0

    for i in [80, 70, 50, 10]:
        distance = np.copy(dist)
        distance[dist < i] = 0

        markers = ndi.label(distance)[0]

        curr_coins = np.max(markers)
        if curr_coins < coins:
            break

        threshold = i
        coins = curr_coins

    if 1 < coins < 10:
        distance = np.copy(dist)
        distance[dist < threshold] = 0

        markers, num_features = ndi.label(distance)
        labels = watershed(-distance, markers, mask=image)

        return labels, num_features

    return None, 0
