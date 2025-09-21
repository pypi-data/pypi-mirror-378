# -*- coding: utf-8 -*-
"""
Provides custom exception classes to handle errors arising from persistence-related operations.

This module defines base and specific exceptions to enable robust error handling in persistence
scenarios. The base class `PersistenceError` covers generic persistence issues, while
`DuplicateKeyError` and `ObjectNotFoundError` address specific cases like duplicate entries
and missing records respectively.
"""

from typing import Any


class PersistenceError(Exception):
    """
    Represents an error related to persistence operations.

    This class is designed to encapsulate errors that occur during persistence
    operations, such as saving or retrieving data. It provides the means to pass
    a custom error message and an optional cause, offering more insight into
    what caused the error. This aids in debugging and understanding context
    in persistence-related failures.
    """

    def __init__(self, message='Persistence error', cause=None):
        """
        Represents an error related to persistence operations.

        This class extends the base Exception class to provide additional context
        for persistence-related errors, allowing an optional cause to be specified.

        :param message: The message describing the error.
        :param cause: The optional cause of the error.
        """
        self.message = message
        self.cause = cause


class DuplicateKeyError(PersistenceError):
    """
    This exception is raised when trying to insert a record with a key that already exists in the data collection.
    """

    def __init__(self, data_collection, key: Any, cause=None):
        """Represents an exception raised when a duplicate key is encountered in a data collection.

        :param data_collection: The data collection in which the duplicate key was encountered.
        :param key: The key that was already present in the data collection.
        """
        super().__init__(f'Duplicate key error : {key} already exist in data collection \'{data_collection}\'.', cause)
        self.data_collection = data_collection
        self.key = key


class ObjectNotFoundError(PersistenceError):
    """
    This exception is raised when trying to find a single record in a data set that does not exist.
    """

    def __init__(self, data_collection, key: Any, cause=None):
        """
        Exception raised when an object is not found in the specified data set for a given key.

        :param data_collection: The data collection in which the object was not found.
        :param key: The key of the object that was not found.
        :param cause: The optional cause of the error.
        """
        super().__init__(f'Not object found with key {key} in data collection \'{data_collection}\'', cause)
        self.data_set = data_collection
        self.key = key
