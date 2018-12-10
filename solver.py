from os import path, mkdir
from skimage import io
import numpy as np

from utils import get_closest_key_from_ratio, decide_if_two_or_five
from items_manager import ItemsManager


class Solver:
    def __init__(self, origin_img_path, output_dir="output"):
        self.origin_img_name = origin_img_path.split("/")[-1]
        self.origin_img = io.imread(origin_img_path)
        self.region_props = ItemsManager(self.origin_img).region_props
        self.output_dir = path.join(output_dir, self.origin_img_name)
        if not path.exists(output_dir):
            mkdir(output_dir)
        if not path.exists(self.output_dir):
            mkdir(self.output_dir)

    def solve(self):
        value_from_not_mono = self.solve_not_mono()
        value_from_mono = self.solve_mono()
        total_value = value_from_mono + value_from_not_mono

        for i, props in enumerate(self.region_props):
            filename = str(i) + "-value-" + str(props.value) + ".png"
            full_path = path.join(self.output_dir, filename)
            io.imsave(full_path, props.color_image)

        return total_value

    def solve_mono(self):
        mono_value = 0
        if ItemsManager.constants.AREAS_MONO and not ItemsManager.constants.ALL_NOT_MONO:
            if ItemsManager.constants.ALL_MONO_SAME:
                # TODO
                if ItemsManager.constants.NOT_MONO_ITEMS:
                    max_not_mono_coin = None
                    max_not_mono_val = 0
                    for item in ItemsManager.constants.NOT_MONO_ITEMS:
                        if item.value > max_not_mono_val:
                            max_not_mono_val = item.value
                            max_not_mono_coin = item
                        if item.value == 5:
                            break
                    if max_not_mono_coin.value == 5:
                        ratio = {0.20: 0.594184028, 0.50: 0.729600694, 1: 0.918402778}
                    else:
                        ratio = {0.20: 0.740400216, 0.50: 0.909140076, 1: 1.14440238}

                    item_areas = [item.area for item in ItemsManager.constants.MONO_ITEMS]
                    mean_item_area = np.mean(item_areas)
                    item_ratio = mean_item_area / max_not_mono_coin.area
                    value = get_closest_key_from_ratio(ratio, item_ratio)
                    for item in ItemsManager.constants.MONO_ITEMS:
                        item.value = value
                        mono_value += value

                else:
                    for item in ItemsManager.constants.MONO_ITEMS:
                        item.value = 1
                        mono_value += 1
                # mono_value = len(ItemsManager.constants.MONO_ITEMS) * wartość_tej_monety
                # no i tez mozna by przypisac wartosc do kazdej monety, zeby sie wyswietlala
            else:
                ratio_for_one_pln = ItemsManager.constants.RATIO_FOR_ONE_PLN
                ratio_for_fifty_gross = ItemsManager.constants.RATIO_FOR_FIFTY_GROSS

                diffs_one = []
                diffs_fifty = []
                for key in ratio_for_one_pln:
                    diff = abs(ItemsManager.constants.RATIO_TEST_MONO - ratio_for_one_pln[key])
                    diffs_one.append(diff)

                for key in ratio_for_fifty_gross:
                    diff = abs(ItemsManager.constants.RATIO_TEST_MONO - ratio_for_fifty_gross[key])
                    diffs_fifty.append(diff)

                if sum(diffs_one) <= sum(diffs_fifty):
                    max_coin_val = 0.5
                else:
                    max_coin_val = 1

                max_coin = [item for item in ItemsManager.constants.MONO_ITEMS if
                            item.area == ItemsManager.constants.MAX_AREA_MONO][0]
                max_coin.value = max_coin_val
                if max_coin.value == 1:
                    ratio = ratio_for_one_pln
                elif max_coin.value == 0.50:
                    ratio = ratio_for_fifty_gross
                else:
                    return 0

                for item in ItemsManager.constants.MONO_ITEMS:
                    item_ratio = item.area / max_coin.area
                    item.value = get_closest_key_from_ratio(ratio, item_ratio)
                    mono_value += item.value

        return mono_value

    def solve_not_mono(self):
        not_mono_value = 0
        if ItemsManager.constants.AREAS_NOT_MONO and not ItemsManager.constants.ALL_MONO:
            if ItemsManager.constants.ALL_NOT_MONO_SAME:
                decisions = [decide_if_two_or_five(item) for item in ItemsManager.constants.NOT_MONO_ITEMS]
                number_of_two_pln = len([i for i in decisions if i == 2])
                number_of_five_pln = len([i for i in decisions if i == 5])
                if number_of_five_pln > number_of_two_pln:
                    final_decision = 5
                else:
                    final_decision = 2
                for item in ItemsManager.constants.NOT_MONO_ITEMS:
                    item.value = final_decision
                not_mono_value += (final_decision * len(ItemsManager.constants.NOT_MONO_ITEMS))
            else:
                for item in ItemsManager.constants.NOT_MONO_ITEMS:
                    if item.area < ItemsManager.constants.MEAN_AREA_NOT_MONO:
                        item.value = 2
                    else:
                        item.value = 5
                    not_mono_value += item.value
        return not_mono_value

