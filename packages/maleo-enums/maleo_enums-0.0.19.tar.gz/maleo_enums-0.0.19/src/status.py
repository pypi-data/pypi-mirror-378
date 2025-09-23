from enum import StrEnum
from typing import List, Optional, Sequence
from maleo.types.string import ListOfStrings


class DataStatus(StrEnum):
    DELETED = "deleted"
    INACTIVE = "inactive"
    ACTIVE = "active"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


OptionalDataStatus = Optional[DataStatus]
ListOfDataStatuses = List[DataStatus]
OptionalListOfDataStatuses = Optional[ListOfDataStatuses]
SequenceOfDataStatuses = Sequence[DataStatus]
OptionalSequenceOfDataStatuses = Optional[SequenceOfDataStatuses]


FULL_DATA_STATUSES: SequenceOfDataStatuses = (
    DataStatus.ACTIVE,
    DataStatus.INACTIVE,
    DataStatus.DELETED,
)

BASIC_DATA_STATUSES: SequenceOfDataStatuses = (
    DataStatus.ACTIVE,
    DataStatus.INACTIVE,
)
