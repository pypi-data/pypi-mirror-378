"""Module that performs statistical operations."""

import math
import statistics
from typing import List


class StatisticalOperations:
    """A class to represent Statistical Operations."""

    @staticmethod
    def is_empty_list(numbers: List[int]) -> bool:
        """Checks whether the list is empty.

        Args:
            numbers (List[int]): List of numbers.

        Returns:
            bool: True if it is empty else False.
        """
        if len(numbers) == 0:
            print("List is empty.")

            return True

        return False

    @staticmethod
    def mean(numbers: List[int]) -> float | None:
        """Finds the mean of the different matrix.

        Args:
            numbers (List[int]): List of numbers for which mean need to be calculated.

        Returns:
            float | None: Mean of the List of numbers.
        """
        if StatisticalOperations.is_empty_list(numbers):
            return None

        return sum(numbers) / len(numbers)

    @staticmethod
    def median(numbers: List[int]) -> int | float | None:
        """Finds the median of the data.

        Args:
            numbers (List[int]): Lis tof numbers for which mode need to be calculated.

        Returns:
            int | float | None: Median of the List of numbers.
        """
        if StatisticalOperations.is_empty_list(numbers):
            return None

        sorted_data = sorted(numbers)
        n = len(sorted_data)
        middle = n // 2

        if n % 2 == 0:
            return (sorted_data[middle - 1] + sorted_data[middle]) / 2

        else:
            return sorted_data[middle]

    @staticmethod
    def mode(numbers: List[int]) -> int | None:
        """Finds the modes of the data.

        Args:
            numbers (List[int]): List of numbers for which modes need to be calculated.

        Returns:
            int | None: List of modes of the numbers.(There can be more than one mode.)
        """
        if StatisticalOperations.is_empty_list(numbers):
            return None

        return statistics.mode(numbers)

    @staticmethod
    def variance(numbers: List[int]) -> float | None:
        """Finds the variance of the data.

        Args:
            numbers (List[int]): List of numbers for which variance need to be calculated.

        Returns:
            float | None: Variance of the numbers.
        """
        if StatisticalOperations.is_empty_list(numbers):
            return None

        mean = StatisticalOperations.mean(numbers)

        if mean:
            return sum((value - mean) ** 2 for value in numbers) / len(numbers)

        return None

    @staticmethod
    def standard_deviation(numbers: List[int]) -> float | None:
        """Finds the standard deviation of the data.

        Args:
            numbers (List[int]): List of numbers for which standard deviation need to be calculated.

        Returns:
            float | None: Standard deviation of the numbers.
        """
        variance = StatisticalOperations.variance(numbers)

        if variance:
            return math.sqrt(variance)

        return None
