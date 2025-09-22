"""Module to represent text file operations."""

import os


class TextFileHandler:
    """A class to handle text file operations."""

    @staticmethod
    def is_text_file(filename: str) -> bool:
        """Checks whether the file is a valid .txt file.

        Args:
            filename (str): Path of the file.

        Returns:
            bool: True if file is a .txt else False
        """
        return filename.endswith(".txt")

    @staticmethod
    def read(filename: str) -> str | None:
        """Reads the entire content of the file and returns as a string.

        Args:
            filename (str): Path of the file.
        """
        if not TextFileHandler.is_text_file(filename):
            print("Not a .txt file.")

            return None

        try:
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()

        except FileNotFoundError:
            print(f"File '{filename}' not found.")

            return None

        except Exception as err:
            print(f"Exception occurred: {err}")

            return None

    @staticmethod
    def write(filename: str, text: str) -> None:
        """Writes the given text to the file, overwriting existing content.

        Args:
            filename (str): Path of the file.
            text (str): Text need to be written in the file.
        """
        if not TextFileHandler.is_text_file(filename):
            print("Not a .txt file.")

            return None

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)

    @staticmethod
    def word_count(filename: str) -> int | None:
        """Returns the total number of words in the file.

        Args:
            filename (str): Path of the file.

        Returns:
            int | None: Count of the words in the file.
        """
        if not TextFileHandler.is_text_file(filename):
            print("Not a .txt file.")

            return None

        content = TextFileHandler.read(filename)

        if content:
            words = content.split()
            return len(words)

        return 0

    @staticmethod
    def find_word(filename: str, word: str) -> int | None:
        """Returns the number of occurrences of the given word in the file (case-insensitive).

        Args:
            filename (str): Path of the file.
            word (str): Word to be counted in the file.

        Returns:
            int | None: Count of the given word occurrence in the file.
        """
        if not TextFileHandler.is_text_file(filename):
            print("Not a .txt file.")

            return None

        content = TextFileHandler.read(filename)

        if content:
            words = content.lower().split()
            return words.count(word.lower())

        return 0

    @staticmethod
    def replace_text(filename: str, old: str, new: str) -> None:
        """Replaces all occurrences of 'old' string with 'new' string in the file.

        Args:
            filename (str): Path of the file.
            old (str): Word to replace.
            new (str): Word to replace with.
        """
        if not TextFileHandler.is_text_file(filename):
            print("Not a .txt file.")

            return None

        content = TextFileHandler.read(filename)

        if content:
            updated_content = content.replace(old, new)
            TextFileHandler.write(filename, updated_content)

    @staticmethod
    def append(filename: str, text: str) -> None:
        """Appends the given text to the end of the file.

        Args:
            filename (str): Path of the filename.
            text (str): Text to be appended on the file.
        """
        if not TextFileHandler.is_text_file(filename):
            print("Not a .txt file.")

            return None

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "a", encoding="utf-8") as f:
            f.write(text)
