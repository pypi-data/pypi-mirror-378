from typing import Iterable, Optional

def find_max(numbers: Iterable[float]) -> Optional[float]:
    """Return the maximum number from the list"""
    nums = list(numbers)
    if not nums:
        return None
    return max(nums)

max_number/init.py

from .core import find_max
