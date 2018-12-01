import numpy as np

from scipy.stats import mode

from skimage import measure, io, exposure, color

from utils import *

from type import Type


class DecisionTree:
    def __init__(self, items):
        self.items = [item for item in items if item.region is not None]
        self.recognized = []
        self.coins = []
        self.mono = []
        self.not_mono = []
        self.unsure = []
        self.all_mono_or_all_not_mono = False

    def solve(self):
        self.prepare_items()
        self.prepare_color_differences()
        self.classify_monochromicity()
        if self.all_mono_or_all_not_mono:
            self.classify_all_mono_or_not_mono()
        else:
            self.classify_mono()
            self.classify_not_mono()
        self.classify_unsure_items()
        score = self.calculate_score()
        return score

    def prepare_items(self):
        for item in self.items:
            if item.is_circle():
                item.circle = True
                if item.is_coin():
                    item.coin = True
                    self.coins.append(item)

    def prepare_color_differences(self):
        color_diffs = []
        for item in self.coins:
            color_diff = calculate_color_difference(item.img)
            item.color_diff = color_diff
            if color_diff > 100:
                color_diffs.append(color_diff)

        if color_diffs:
            color_diff_border = sum(color_diffs) / len(color_diffs)
            diff_from_border = sum(([abs(color_diff_border - x) for x in color_diffs]))
            parameter = diff_from_border / color_diff_border / len(color_diffs)
            if parameter < 0.2:
                for item in self.items:
                    item.color_diff_border = 0
                    item.color_diff = 0
            else:
                for item in self.items:
                    item.color_diff_border = color_diff_border

    def classify_monochromicity(self):
        for item in self.coins:
            result = item.classify()
            if result == Type.UNSURE:
                self.unsure.append(item)
            elif result == Type.MONOCHROMATIC_COIN:
                self.mono.append(item)
            elif result == Type.NOT_MONOCHROMATIC_COIN:
                self.not_mono.append(item)
            elif result == Type.ALL_MONO_OR_ALL_NOT_MONO:
                self.all_mono_or_all_not_mono = True
                break

    def classify_mono(self):
        sizes = [item.size for item in self.mono]
        if sizes:
            std = np.std(np.array(sizes))
            max_size = max(sizes)
            if std < max_size / 12:
                # TODO: to znaczy, ze monety sa takie same. Byc moze trzeba dopracowac te liczbe
                pass
            else:
                ratio_for_one_pln = {0.20: 0.646974096, 0.50: 0.79442282, 1: 1} # for size (area)
                ratio_for_fifty_gross = {0.20: 0.814396149, 0.50: 1, 1: 1.258774046}

                ratio_test = min(sizes) / max_size
                min_diff = 1
                max_coin_val = 0
                for key in ratio_for_one_pln:
                    diff = abs(ratio_test - ratio_for_one_pln[key])
                    if diff <= min_diff:
                        min_diff = diff
                        max_coin_val = 1

                for key in ratio_for_fifty_gross:
                    diff = abs(ratio_test - ratio_for_fifty_gross[key])
                    if diff <= min_diff:
                        min_diff = diff
                        max_coin_val = 0.50

                max_coin = [item for item in self.mono if item.size == max_size][0]
                max_coin.value = max_coin_val
                if max_coin.value == 1:
                    ratio = ratio_for_one_pln
                elif max_coin.value == 0.50:
                    ratio = ratio_for_fifty_gross
                else:
                    return

                for item in self.mono:
                    item_ratio = item.size / max_coin.size
                    item.value = get_closest_key_from_ratio(ratio, item_ratio)
                    self.recognized.append(item)

    def classify_not_mono(self):
        sizes = [item.size for item in self.not_mono]
        if sizes:
            std = np.std(np.array(sizes))
            max_size = max(sizes)
            # if std < (max_size - min(sizes)):
            if np.mean(np.array(sizes))*0.05 <= max(sizes)-max(sizes) <= np.mean(np.array(sizes))*0.06:
                # TODO: tutaj wszystkie monety sa takie same. Byc moze trzeba zmienic troche liczbe
                decisions = [decide_if_two_or_five(item) for item in self.not_mono]
                number_of_two_pln = len([i for i in decisions if i == 2])
                number_of_five_pln = len([i for i in decisions if i == 5])
                if number_of_five_pln > number_of_two_pln:
                    final_decision = 5
                else:
                    final_decision = 2
                for item in self.not_mono:
                    item.value = final_decision
                    self.recognized.append(item)
            else:
                avg_size = sum(sizes) / len(sizes)
                for item in self.not_mono:
                    if item.size < avg_size:
                        item.value = 2
                        self.recognized.append(item)
                    else:
                        item.value = 5
                        self.recognized.append(item)

    def classify_all_mono_or_not_mono(self):
        percentages = []
        for item in self.coins:
            avg_red = np.mean(item.img[:, :, 0])
            avg_green = np.mean(item.img[:, :, 1])
            avg_blue = np.mean(item.img[:, :, 2])
            avg_all = np.mean(item.img[:, :, :3])
            diffs = abs(avg_red - avg_green) + abs(avg_green - avg_blue)
            percentage = diffs / avg_all
            percentages.append(percentage)

        if np.mean(np.array(percentages)) < 0.13:
            self.mono = self.coins
            self.classify_mono()
        else:
            self.not_mono = self.coins
            self.classify_not_mono()

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
