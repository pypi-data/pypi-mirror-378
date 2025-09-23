from enum import StrEnum
from typing import List, Optional, Sequence
from maleo.types.string import ListOfStrings


class Order(StrEnum):
    ASC = "asc"
    DESC = "desc"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


OptionalOrder = Optional[Order]
ListOfOrders = List[Order]
OptionalListOfOrders = Optional[ListOfOrders]
SequenceOfOrders = Sequence[Order]
OptionalSequenceOfOrders = Optional[SequenceOfOrders]
