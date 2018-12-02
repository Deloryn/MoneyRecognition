from utils import calculate_distances_from_centroid


class Contour:
    def __init__(self, coords):
        self.coords = coords
        self.x = [x for x, y in coords]
        self.y = [y for x, y in coords]

        min_x = min(self.x)
        max_x = max(self.x)
        min_y = min(self.y)
        max_y = max(self.y)

        self.width = max_x - min_x
        self.height = max_y - min_y

        self.centroid = [(min_x + max_x) / 2, (min_y + max_y) / 2]

        self.distances_from_centroid = calculate_distances_from_centroid(self.coords, self.centroid)
        self.min_distance = min(self.distances_from_centroid)
        self.max_distance = max(self.distances_from_centroid)
        self.mean_distance = sum(self.distances_from_centroid) / len(self.distances_from_centroid)

    def is_circle(self):
        if self.mean_distance < (self.width / 2) * 1.15 and self.mean_distance < (
                self.height / 2) * 1.15 and self.max_distance / self.min_distance < 1.4:
            return True
        else:
            return False
