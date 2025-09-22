"""Module to perform matrix operations."""

from typing import List

import numpy as np


class MatrixOperations:
    """A class to do the matrix operations."""

    @staticmethod
    def matrix_initialization(row: int, col: int) -> List[List[int]]:
        """Initialization matrix with the given rows and columns.

        Args:
            row (int): No of rows in the resultant matrix.
            col (int): No of columns in the resultant matrix.

        Returns:
            List[List[int]]: Resultant Matrix initialized with zeros.
        """
        return [[0 for _ in range(col)] for _ in range(row)]

    @staticmethod
    def matrix_multiplication(
        matrix1: List[List[int]], matrix2: List[List[int]]
    ) -> List[List[int]] | None:
        """Multiplies two given matrix.

        Args:
            matrix1 (List[List[int]]): First Matrix.
            matrix2 (List[List[int]]): Second Matrix.

        Returns:
            List[List[int]] | None: The result of the two given matrices multiplied.
        """
        row_matrix1 = len(matrix1)
        col_matrix1 = len(matrix1[0])
        row_matrix2 = len(matrix2)
        col_matrix2 = len(matrix2[0])

        if col_matrix1 != row_matrix2:
            print("Cannot multiply these two matrices.")

            return None

        result: List[List[int]] = MatrixOperations.matrix_initialization(col_matrix1, row_matrix2)
        for index1 in range(row_matrix1):
            for index2 in range(col_matrix2):
                for index3 in range(row_matrix2):
                    result[index1][index2] += matrix1[index1][index3] * matrix2[index3][index2]

        return result

    @staticmethod
    def is_empty_matrix(matrix: List[List[int]]) -> bool:
        """Checks whether the matrix is empty.

        Args:
            matrix (List[List[int]]): Matrix to check.

        Returns:
            bool: True if empty else false.
        """
        return len(matrix) == 0

    @staticmethod
    def is_square_matrix(matrix: List[List[int]]) -> bool | None:
        """Finds whether the matrix is square matrix.

        Args:
            matrix (List[List[int]]): The matrix that need to be checked.

        Returns:
            bool | None: True if square matrix else False.
        """
        if MatrixOperations.is_empty_matrix(matrix):
            print("Empty matrix cannot be square matrix.")

            return None

        return len(matrix) == len(matrix[0])

    @staticmethod
    def find_eigen_values(matrix: List[List[int]]) -> List[float] | None:
        """Finds the eigen values of the square matrix.

        Args:
            matrix (List[List[int]]): Square matrix that we need to calculate eigenvalues.

        Returns:
        List[List[float]] | None: Eigenvalues if found.
        """
        if MatrixOperations.is_square_matrix(matrix):
            eigenvalues = np.linalg.eigvals(matrix)
            result: List[float] = []

            for element in eigenvalues:
                result.append(float(element))

            return result

        print("The matrix has to be square matrix.")
        return None

    @staticmethod
    def transpose_matrix(matrix: List[List[int]]) -> List[List[int]]:
        """Gives the transpose of a matrix.

        Args:
            matrix (List[List[int]]): Matrix that needs to be transposed.

        Returns:
            List[List[int]]: Transposed matrix.
        """
        return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]
