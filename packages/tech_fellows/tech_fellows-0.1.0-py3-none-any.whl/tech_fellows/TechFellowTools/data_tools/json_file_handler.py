"""Module to represent JSON operations."""

import json
import os
from typing import Dict


class JsonHandler:
    """A class to handle json files."""

    @staticmethod
    def is_json_file(filename: str) -> bool:
        """Checks whether the file is a valid .json file.

        Args:
            filename (str): Path of the file.

        Returns:
            bool: True if file is a .json else False
        """
        return filename.endswith(".json")

    @staticmethod
    def read_json(filepath: str) -> Dict[str, str] | None:
        """Read and return JSON data from the file.

        Args:
            filepath (str): Path of the JSON file.

        Returns:
            Dict[str, str] | None: Data of the file.

        Raises:
            FileNotFoundError: When the file is not found.
            ValueError: Content is not a valid JSON.
        """
        if not JsonHandler.is_json_file(filepath):
            print("Not a .json file.")

            return None

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No such JSON file: {filepath}")

        with open(filepath, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)

                return data

            except json.JSONDecodeError as e:
                raise ValueError(f"File content is not valid JSON: {e}") from e

    @staticmethod
    def write_json(filepath: str, data: Dict[str, str]) -> None:
        """Write Python data as JSON into the file.

        Args:
            filepath(str): Path of the file.
            data (Dict[str, str]): Data to write on the file.
        """
        if not JsonHandler.is_json_file(filepath):
            print("Not a .json file.")

            return None

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    @staticmethod
    def update_json(filepath: str, key: str, value: str) -> None:
        """Update a specific key in the JSON data and save back.

        Args:
            filepath (str) : Path of the JSON file.
            key (str): Key in the JSON where data need to be updated.
            value (str): Value to be updated.

        Raises:
            TypeError: If JSON root element is not a dictionary.
        """
        if not JsonHandler.is_json_file(filepath):
            print("Not a .json file.")

            return None

        data = JsonHandler.read_json(filepath)
        if isinstance(data, dict):
            data[key] = value
            JsonHandler.write_json(filepath, data)

        else:
            raise TypeError("JSON root element must be a dictionary to update keys.")

    @staticmethod
    def append(filepath: str, new_element: Dict[str, str]) -> None:
        """Append an element in the JSON file.

        The root JSON should be a list or contain a list under some known key.

        Args:
            filepath (str): Path of the JSON file.
            new_element (Dict[str, str]): New element to add in the JSON file.
        """
        if not JsonHandler.is_json_file(filepath):
            print("Not a .json file.")

            return None

        data: Dict[str, str] | None = JsonHandler.read_json(filepath)

        if isinstance(data, Dict):
            data.update(new_element)
            JsonHandler.write_json(filepath, data)

        else:
            raise TypeError("JSON root element must be a Dictionary to append elements.")

    @staticmethod
    def exists_and_valid(filepath: str) -> bool | None:
        """Check whether the file exists and contains valid JSON.

        Args:
            filepath (str): Path of the json file.

        Returns:
            bool | None: Checks whether the path is valid.
        """
        if not JsonHandler.is_json_file(filepath):
            print("Not a .json file.")

            return None

        if not os.path.exists(filepath):
            return False
        try:
            JsonHandler.read_json(filepath)
            return True

        except Exception:
            return False
