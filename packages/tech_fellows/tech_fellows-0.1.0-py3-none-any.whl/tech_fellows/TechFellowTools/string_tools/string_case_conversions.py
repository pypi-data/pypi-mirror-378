"""Module to perform various operations on string."""


class StringCaseOperations:
    """A class to represent string case conversions."""

    @staticmethod
    def convert_to_upper_case(input_string: str) -> str:
        """Converts the given string to upper case.

        Args:
            input_string (str): Input string.

        Returns:
            str: Result string converted in upper case.
        """
        return input_string.upper()

    @staticmethod
    def convert_to_lower_case(input_string: str) -> str:
        """Converts the given string to lower case.

        Args:
            input_string (str): Input string.

        Returns:
            str: Result string converted in lower case..
        """
        return input_string.lower()

    @staticmethod
    def capitalize(input_string: str) -> str:
        """Converts the given string case to capitalize.

        Args:
            input_string (str): Input string.

        Returns:
            str: Result string by capitalizing.
        """
        return input_string.capitalize()

    @staticmethod
    def title_case(input_string: str) -> str:
        """Converts the given string to lower case.

        Args:
            input_string (str): Input string.

        Returns:
            str: Result string which have every first word in upper case.
        """
        return input_string.title()

    @staticmethod
    def swap_case(input_string: str) -> str:
        """Swaps the case.

        Args:
            input_string (str): Input string.

        Returns:
            str: Result string where the casing is reversed.
        """
        return input_string.swapcase()
