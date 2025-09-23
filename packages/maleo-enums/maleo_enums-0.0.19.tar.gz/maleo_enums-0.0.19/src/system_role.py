from enum import StrEnum
from maleo.types.string import ListOfStrings


class Key(StrEnum):
    ADMINISTRATOR = "administrator"
    ANALYST = "analyst"
    ENGINEER = "engineer"
    SUPPORT = "support"
    MANAGER = "manager"
    OFFICER = "officer"
    OPERATIONS = "operations"
    SECURITY = "security"
    TESTER = "tester"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]
