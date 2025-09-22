# -*- coding: utf-8 -*-
"""
Encapsulates results of various database operations including delete, update, insert, and replace.

The module defines specialized classes for operation results, providing detailed insights
into the execution of common database actions. Each class represents a specific type of
database action and provides structured access to the results, including the count of records affected
and any associated raw data.
"""

from typing import Any

from monkey.dao import OperationType


#TODO: Review classes from pymongo.results module to enhance OperationResult speciations

class OperationResult:
    """
    Represents the result of an operation.

    This class contains details of the operation result, including the type of operation, the number of records
    involved, and the raw result.

    :ivar op_type: The type of the operation.
    :type op_type: OperationType
    :ivar rec_count: The number of records involved in the operation.
    :type rec_count: int
    :ivar raw_result: The raw result of the operation. It depends on the data source and the operation type.
    :type raw_result: Any
    """

    def __init__(self, op_type: OperationType, rec_count: int, raw_result: Any):
        """
        Initializes the instance. Used for creating an object encapsulating the result details of a specific operation.

        :param op_type: The specific operation type being performed.
        :param rec_count: The count of records involved in the operation.
        :param raw_result: The raw result data or object returned from the operation.
        """
        self.op_type = op_type
        self.rec_count = rec_count
        self.raw_result = raw_result


class DeleteResult(OperationResult):
    """
    Represents the outcome of a delete operation.

    This class is used to encapsulate the result of a delete operation, including
    the count of records deleted and any additional raw.

    :ivar rec_count: The number of records successfully deleted.
    :type rec_count: int
    :ivar raw_result: The raw result returned from the delete operation, if any.
    :type raw_result: Any
    """

    def __init__(self, rec_count: int, raw_result: Any = None):
        """
        Initializes an instance of the class with details regarding a delete operation.

        :param rec_count: The number of records affected by the operation.
        :param raw_result: The raw data resulting from the operation execution for further processing or storage.
            Defaults to None.
        """
        super().__init__(OperationType.DELETE, rec_count, raw_result)

    @property
    def deleted_count(self) -> int:
        """
        This property provides access to the count of records that have been marked or
        processed as deleted. It is expected to return the current count of such records,
        which is represented internally by a tracked attribute.

        :return: The number of records that have been marked as deleted.
        """
        return self.rec_count


class UpdateResult(OperationResult):
    """
    Represents the result of an update operation.

    Provides detailed information about the outcome of the update operation, including the count of records updated and
    whether an upsert occurred.

    :ivar did_upsert: Indicates whether the operation resulted in an upsert
        (insert if not found).
    """

    def __init__(self, rec_count: int, raw_result: Any, did_upsert: bool = False):
        """
        Initializes an instance of the class with details regarding an update operation.

        :param rec_count: The number of records affected by the update operation.
        :param raw_result: The raw result returned from the database operation.
        :param did_upsert: Indicates if the operation resulted in an upsert to the database. Defaults to False.
        """
        super().__init__(OperationType.UPDATE, rec_count, raw_result)
        self.did_upsert = did_upsert

    @property
    def updated_count(self) -> int:
        """
        Provides the number of records that have been updated.

        :return: The count of updated records.
        """
        return self.rec_count


class InsertResult(OperationResult):
    """
    Represents the result of an insert operation.

    This class is a specialization of the OperationResult class, specifically
    to capture the result of an insert operation. It provides additional
    details pertinent to the inserted data and encapsulates the result
    as returned by the insert operation.
    """

    def __init__(self, rec_count: int, raw_result: Any):
        """
        Initializes an instance of the class with details regarding an insert operation.

        :param rec_count: Number of records to be inserted.
        :param raw_result: Raw data or result object associated with the
            operation.
        """
        super().__init__(OperationType.INSERT, rec_count, raw_result)

    @property
    def inserted_count(self) -> int:
        """
        Provides access to the number of records inserted into the database or a relevant storage.

        :return: The count of records inserted so far.
        """
        return self.rec_count


class ReplaceResult(OperationResult):
    """
    Represents the result of a replace operation.

    This class extends OperationResult and is specifically designed to handle
    the results of a document replace operation. It includes functionality to
    track whether records were upserted as part of the replacement action.

    :ivar did_upsert: Indicates if an upsert operation occurred during the replacement process.
    :type did_upsert: bool
    """

    def __init__(self, rec_count: int, raw_result: Any, did_upsert: bool = False):
        """
        Initializes an instance of the class with details regarding a replace operation.

        :param rec_count: The number of records affected by the replace operation.
        :param raw_result: Raw result object containing the replace operation's
            detailed outcome.
        :param did_upsert: Indicates whether the replace operation resulted in an
            upsert (insert if no record exists). Default is False.
        """
        super().__init__(OperationType.REPLACE, rec_count, raw_result)
        self.did_upsert = did_upsert

    @property
    def replaced_count(self) -> int:
        """
        Provides access to the count of records that have been replaced.

        :return: The count of records replaced.
        """
        return self.rec_count
