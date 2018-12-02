from os import path, mkdir

from skimage import io

from utils import get_closest_key_from_ratio, decide_if_two_or_five

from items_manager import ItemsManager


class Solver:
    def __init__(self, origin_img_path, output_dir="output"):
        self.origin_img_name = origin_img_path.split("/")[-1]
        self.origin_img = io.imread(origin_img_path)
        self.items_manager = ItemsManager(self.origin_img)
        self.output_dir = path.join(output_dir, self.origin_img_name)
        if not path.exists(output_dir):
            mkdir(output_dir)
        if not path.exists(self.output_dir):
            mkdir(self.output_dir)

    def solve(self):
        value_from_mono = self.solve_mono()
        value_from_not_mono = self.solve_not_mono()
        total_value = value_from_mono + value_from_not_mono

        for i, item in enumerate(self.items_manager.items):
            item.save_img(self.output_dir, i)

        return total_value

    def solve_mono(self):
        mono_value = 0
        if ItemsManager.constants.AREAS_MONO:
            if ItemsManager.constants.ALL_MONO_SAME:
                # TODO
                pass
                # mono_value = len(ItemsManager.constants.MONO_ITEMS) * wartość_tej_monety
                # no i tez mozna by przypisac wartosc do kazdej monety, zeby sie wyswietlala
            else:
                ratio_for_one_pln = ItemsManager.constants.RATIO_FOR_ONE_PLN
                ratio_for_fifty_gross = ItemsManager.constants.RATIO_FOR_FIFTY_GROSS

                min_diff = 1
                max_coin_val = 0
                for key in ratio_for_one_pln:
                    diff = abs(ItemsManager.constants.RATIO_TEST_MONO - ratio_for_one_pln[key])
                    if diff <= min_diff:
                        min_diff = diff
                        max_coin_val = 1

                for key in ratio_for_fifty_gross:
                    diff = abs(ItemsManager.constants.RATIO_TEST_MONO - ratio_for_fifty_gross[key])
                    if diff <= min_diff:
                        min_diff = diff
                        max_coin_val = 0.50

                max_coin = [item for item in ItemsManager.constants.MONO_ITEMS if
                            item.region.area == ItemsManager.constants.MAX_AREA_MONO][0]
                max_coin.value = max_coin_val
                if max_coin.value == 1:
                    ratio = ratio_for_one_pln
                elif max_coin.value == 0.50:
                    ratio = ratio_for_fifty_gross
                else:
                    return

                for item in ItemsManager.constants.MONO_ITEMS:
                    item_ratio = item.region.area / max_coin.region.area
                    item.value = get_closest_key_from_ratio(ratio, item_ratio)
                    mono_value += item.value

        return mono_value

    def solve_not_mono(self):
        not_mono_value = 0
        if ItemsManager.constants.AREAS_NOT_MONO:
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
                    if item.region.area < ItemsManager.constants.MEAN_AREA_NOT_MONO:
                        item.value = 2
                    else:
                        item.value = 5
                    not_mono_value += item.value
        return not_mono_value

