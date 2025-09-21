# -*- coding: utf-8 -*-
"""
Provides a generic specification for implementing the Data Access Object (DAO) design model.

The term 'data collection' refers to either a table in a relational database or a document in a NoSQL database.

This speciation will have to be implemented by each database system.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Iterable, Union

from monkey.dao.results import DeleteResult, UpdateResult, InsertResult, ReplaceResult


class DAO(ABC):
    """
    Generic definition of Data Access Object.

    This class defines a common interface for all DAOs, so most methods will have to be overridden in subclasses,
    depending on the type of data collection used.

    The methods are designed to be generic and abstract, allowing the implementation to be changed or extended.
    Most of theses methods accept a **kwargs parameter that can be used to pass additional arguments to the underlying
    implementation.
    """

    def __init__(self):
        """
        Instantiates a new DAO.
        """
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def find(self, query: Any = None, skip: int = 0, limit: int = 0, sort: Union[None, dict[str, int]] = None,
             **kwargs):
        """
        Finds records matching the specified query.

        This method is intended to be overridden by subclasses to provide
        specific logic for retrieving records matching the query from a data collection.
        If no matching record is found, the method returns an empty list.

        :param query: The filter used to query the data collection. If the query is None, all records are returned.
        :param skip: The number of records to omit (from the start of the result set) when returning the results.
        :param limit: The maximum number of records to return.
        :param sort: A list of (field key, direction) pairs specifying the sort order for this list. For sort direction, use 1 for ascending and -1 for descending.
        :param kwargs: Implementation specific arguments.
        :return: The list of query matching records.
        """
        pass

    def find_all(self, skip: int = 0, limit: int = 0, sort: Union[None, dict[str, int]] = None, **kwargs):
        """
        Finds all the records in the data collection.
        :param skip: The number of records to omit (from the start of the result set) when returning the results.
        :param limit: The maximum number of records to return.
        :param sort: A list of (key, direction) pairs specifying the sort order for this list.
        :param kwargs: Implementation specific arguments.
        :return: The list of all records.
        """
        return self.find(query=None, skip=skip, limit=limit, sort=sort, **kwargs)

    @abstractmethod
    def find_one(self, query: Any = None, **kwargs):
        """
        Finds a single record in the data collection that matches the given query.

        This method is intended to be overridden by subclasses to provide
        specific logic for retrieving a single record from a data collection.
        If no matching record is found, the method may raise an ObjectNotFound error.

        :param query: The filter used to query the data collection. If the query is None, the first found record is returned.
        :param kwargs: Implementation specific arguments.
        :return: The record matching the query.
        :raises ObjectNotFoundError: If no record matches the given query.
        """
        pass

    @abstractmethod
    def find_one_by_key(self, key: Any, **kwargs):
        """
        Finds a record by its key.

        This method is intended to be overridden by subclasses to provide
        specific logic for retrieving a single identified record from a data collection.
        If no matching record is found, the method may raise an ObjectNotFound error.

        :param key: The key of the record.
        :param kwargs: Implementation specific arguments.
        :return: The found record (if there is one).
        :raises ObjectNotFoundError: If no records match the specified key.
        """
        pass

    @abstractmethod
    def count(self, query: Any = None, **kwargs) -> int:
        """
        Counts the number of records matching the query.

        This method is intended to be overridden by subclasses to provide
        specific logic for counting records matching the query from a data collection.

        :param query: The filter used to query the data collection.
        :param kwargs: Implementation specific arguments.
        :return: The total number of records.
        """
        pass

    def count_all(self, **kwargs) -> int:
        """
        Counts the number of all records.
        :param kwargs: Implementation specific arguments.
        :return: The total number of records.
        """
        return self.count(query=None, **kwargs)

    @abstractmethod
    def delete(self, query: Any = None, **kwargs) -> DeleteResult:
        """
        Deletes the record identified by the given key.

        This method is intended to be overridden by subclasses to provide
        specific logic for deleting a single record from a data collection.

        :param query: The filter used to query the records to be deleted from the data collection.
        :param kwargs: Implementation specific arguments.
        :return: An instance of DeleteResult.
        """
        pass

    @abstractmethod
    def delete_one(self, query: Any = None, **kwargs) -> DeleteResult:
        """
        Deletes the first record matching the query.

        This method is intended to be overridden by subclasses to provide
        specific logic for deleting a single record matching the query from a data collection.
        The number of deleted records must always be 1 or 0 whether no records correspond to the filter request.

        :param query: The query filter to select the record to be deleted from the data collection.
        :param kwargs: Implementation specific arguments.
        :return: An instance of DeleteResult.
        """
        pass

    def delete_all(self, **kwargs) -> DeleteResult:
        """
        Deletes all records from the associated collection or data set.

        This method invokes the `delete` function internally to remove all
        records by passing a `None` query: Any, meaning no specific filters are
        applied during the deletion. You can provide additional options or
        parameters for the deletion process via the keyword arguments.

        :param kwargs: Implementation specific arguments.
        :return: An instance of `DeleteResult` which contains information
            about the deletion operation, including status and other details.
        """
        return self.delete(query=None, **kwargs)

    @abstractmethod
    def delete_one_by_key(self, key: Any, **kwargs) -> DeleteResult:
        """Deletes the record identified by the given key.

        This method is intended to be overridden by subclasses to provide
        specific logic for deleting a single identified record from a data collection.
        It returns 1 if the record was deleted, 0 otherwise.

        :param key: The key of the record is to delete.
        :param kwargs: Implementation specific arguments.
        :return: An instance of DeleteResult.
        """
        pass

    @abstractmethod
    def insert(self, data: Iterable[Any], **kwargs) -> InsertResult:
        """
        Inserts many new records into the data collection.

        This method is intended to be overridden by subclasses to provide
        specific logic for inserting a list of new records into the data collection.
        It returns a dataset representing the inserted record.

        :param data: The list of data to insert as new records.
        :param kwargs: Implementation specific arguments.
        :return: An instance of InsertResult.
        :raises DuplicateKeyError: If trying to insert a record with a key that already exists in the data collection.
        """
        pass

    def insert_one(self, data: Any, **kwargs) -> InsertResult:
        """
        Inserts a new record into the data collection.
        
        This method is intended to be overridden by subclasses to provide
        specific logic for inserting a single record into the data collection.

        :param data: The data to insert.
        :param kwargs: Implementation specific arguments.
        :return: An instance of InsertResult.
        :raises DuplicateKeyError: If trying to insert a record with a key that already exists in the data collection.
        """
        return self.insert([data], **kwargs)

    @abstractmethod
    def update(self, query: Any, change_set: Any, upsert: bool = False, **kwargs) -> UpdateResult:
        """
        Updates many records in the database matching the provided query. The
        method will apply the given modifications defined in the data parameter.
        
        This method is intended to be overridden in a subclass to provide
        specific logic for updating many records into the data collection.

        :param query: The query used to filter records to update. Must define the matching
            criteria to find desired records.
        :param change_set: The modifications to apply to the matched records. Can include new values
            or transformations.
        :param upsert: Determines whether to insert a new document if no matching record exists.
            Defaults to False.
        :param kwargs: Implementation specific arguments.
        :return: Returns an instance of UpdateResult.
        """
        pass

    @abstractmethod
    def update_one(self, key: Any, change_set: Any, upsert: bool = False, **kwargs) -> UpdateResult:
        """
        Updates the record associated with the given key using provided data.

        This method is intended to be overridden in a subclass to provide
        specific logic for updating a single identified record into the data collection.

        :param key: The key of the record is to update.
        :param change_set: The data to update.
        :param upsert: If True, the record will be inserted if it does not exist.
        :param kwargs: Implementation specific arguments.
        :return: An instance of UpdateResult.
        """
        pass

    @abstractmethod
    def replace(self, query: Any, data: Any, upsert: bool = False, **kwargs) -> ReplaceResult:
        """
        Replaces a document in the database with the provided `data` based on
        the specified `query`. If the `upsert` option is enabled and no document
        matches the `query`, a new document will be inserted.

        :param query: The search query used to locate the document that will
            be replaced. This determines the condition for document matching.
        :param data: The new data that will replace the matched document. This
            should be in an acceptable format for the database.
        :param upsert: A flag indicating whether to perform an "upsert" operation.
            If True, a new document is created when no matching document is found.
            Defaults to False.
        :param kwargs: Additional optional keyword arguments that may be required
            by the implementation.
        :return: A result object containing details of the replace operation,
            such as success status, number of modified rows, or information about
            an upserted document.
        """
        pass

    @abstractmethod
    def replace_one(self, key: Any, data: Any, upsert: bool = False, **kwargs) -> ReplaceResult:
        """
        Replaces the record associated with the given key using provided data.

        This method is intended to be implemented by subclasses to provide the
        specific behavior for replacing a single identified record into the data collection. 
        It returns a dataset representing the replaced record.
        The key identifier has to be preserved during the replacement.

        :param key: The key of the record to replace.
        :param data: The data to replace.
        :param upsert: If True, the record will be inserted if it does not exist.
        :param kwargs: Implementation specific arguments.
        :return: An instance of ReplaceResult.
        """
        pass
