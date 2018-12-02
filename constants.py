import numpy as np


class Constants:
    def __init__(self, areas, mean_color_amplitude, coins_color_diffs_percentages, all_mono_or_not_mono, mono_items, not_mono_items, mono_or_not_mono_items):
        self.RATIO_FOR_ONE_PLN = {0.20: 0.646974096, 0.50: 0.79442282, 1: 1}
        self.RATIO_FOR_FIFTY_GROSS = {0.20: 0.814396149, 0.50: 1, 1: 1.258774046}
        self.MEAN_COLOR_AMPLITUDE = mean_color_amplitude
        self.AREAS = np.array(areas)
        self.MAX_AREA = max(areas)
        self.MIN_AREA = min(areas)
        self.STD_AREAS = np.std(self.AREAS)
        self.MEAN_AREAS = np.mean(self.AREAS)
        self.MEAN_COINS_COLOR_DIFFS_PERCENTAGE = np.mean(np.array(coins_color_diffs_percentages))
        self.ALL_MONO_OR_NOT_MONO = all_mono_or_not_mono
        self.ALL_MONO_SAME = False
        self.ALL_NOT_MONO_SAME = False
        self.MONO_ITEMS = mono_items
        self.NOT_MONO_ITEMS = not_mono_items
        self.MONO_OR_NOT_MONO_ITEMS = mono_or_not_mono_items
        self.COINS = mono_items + not_mono_items + mono_or_not_mono_items

        if self.MEAN_COINS_COLOR_DIFFS_PERCENTAGE < 0.13 and self.ALL_MONO_OR_NOT_MONO:
            self.ALL_MONO = True
            self.ALL_NOT_MONO = False
            self.MONO_ITEMS = self.COINS
        else:
            self.ALL_MONO = False
            self.ALL_NOT_MONO = True
            self.NOT_MONO_ITEMS = self.COINS

        self.AREAS_MONO = [item.region.area for item in self.MONO_ITEMS]
        if self.AREAS_MONO:
            self.STD_AREAS_MONO = np.std(np.array(self.AREAS_MONO))
            self.MAX_AREA_MONO = max(self.AREAS_MONO)

            if self.STD_AREAS_MONO < self.MAX_AREA_MONO / 12:
                # TODO: to znaczy, ze monety sa takie same. Byc moze trzeba dopracowac te liczbe
                self.ALL_MONO_SAME = True
            else:
                self.MIN_AREA_MONO = max(self.AREAS_MONO)
                self.RATIO_TEST_MONO = self.MIN_AREA_MONO / self.MAX_AREA_MONO

        self.AREAS_NOT_MONO = [item.region.area for item in self.NOT_MONO_ITEMS]
        if self.AREAS_NOT_MONO:
            self.STD_AREAS_NOT_MONO = np.std(np.array(self.AREAS_NOT_MONO))
            self.MAX_AREA_NOT_MONO = max(self.AREAS_NOT_MONO)
            self.MIN_AREA_NOT_MONO = min(self.AREAS_NOT_MONO)
            self.MEAN_AREA_NOT_MONO = np.mean(np.array(self.AREAS_NOT_MONO))
            if self.MEAN_AREA_NOT_MONO * 0.05 <= self.MAX_AREA_NOT_MONO - self.MIN_AREA_NOT_MONO <= self.MEAN_AREA_NOT_MONO * 0.06:
                # TODO: tutaj wszystkie monety sa takie same. Byc moze trzeba zmienic troche liczbe
                self.ALL_NOT_MONO_SAME = True
