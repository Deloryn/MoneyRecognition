from enum import Enum


class Type(Enum):
    MONOCHROMATIC_COIN = 0
    NOT_MONOCHROMATIC_COIN = 1
    ALL_MONO_OR_ALL_NOT_MONO = 2
    REJECTED = 3
    UNSURE = 4
    MULTISHAPE = 5
    TWENTY_GROSS = 6
    FIFTY_GROSS = 7
    ONE_PLN = 8
    TWO_PLN = 9
    FIVE_PLN = 10
    TWENTY_PLN = 11
    FIFTY_PLN = 12
