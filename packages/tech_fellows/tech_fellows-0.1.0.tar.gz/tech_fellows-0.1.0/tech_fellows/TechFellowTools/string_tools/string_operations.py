"""Module to perform various string operations."""

from typing import List


class StringOperations:
    """A class to represent string operations."""

    @staticmethod
    def utf_encoding(input_string: str) -> bytes:
        """Encodes the string into bytes using  utf-8 .

        Args:
            input_string (str): Input string.

        Returns:
            bytes: utf-8 encoding of given string.
        """
        return input_string.encode("utf-8")

    @staticmethod
    def utf_decoding(input_bytes: bytes) -> str:
        """Decodes the bytes back into a string.

        Args:
            input_bytes (bytes): Encoded bytes.

        Returns:
            str: Decoded string.
        """
        return input_bytes.decode("utf-8")

    @staticmethod
    def replace_substring(input_string: str, substring: str, new_string: str) -> str:
        """Replaces all the occurrences of substring in a string.

        Args:
            input_string (str): Input string in which substring should be replaced.
            substring (str): Substring to replace.
            new_string (str): New substring.

        Returns:
            str: Replaced string.
        """
        return input_string.replace(substring, new_string)

    @staticmethod
    def is_numeric(input_string: str) -> bool:
        """Checks if given string is integer.

        Args:
            input_string (str): String to check.

        Returns:
            bool: True if given string is numeric.
        """
        try:
            float(input_string)
            return True

        except ValueError:
            return False

    @staticmethod
    def join_strings(strings_list: List[str]) -> str:
        """Joins the strings in the list.

        Args:
            strings_list (List[str]): List of string.

        Returns:
            str: Joined string.
        """
        return " ".join(strings_list)
