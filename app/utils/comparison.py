from enum import Enum


class Comparison(Enum):
    GREATER = "greater"
    LESS = "less"

    def compare(self, reading: float, bound: float) -> bool:
        if self == Comparison.GREATER:
            return reading > bound
        elif self == Comparison.LESS:
            return reading < bound
        return False
