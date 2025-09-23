from enum import StrEnum
from typing import List, Optional, Sequence
from maleo.types.string import ListOfStrings


class Environment(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


OptionalEnvironment = Optional[Environment]
ListOfEnvironments = List[Environment]
OptionalListOfEnvironments = Optional[ListOfEnvironments]
SequenceOfEnvironments = Sequence[Environment]
OptionalSequenceOfEnvironments = Optional[SequenceOfEnvironments]
