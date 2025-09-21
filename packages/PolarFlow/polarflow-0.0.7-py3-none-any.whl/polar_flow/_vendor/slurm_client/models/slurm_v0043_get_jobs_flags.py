from enum import Enum


class SlurmV0043GetJobsFlags(str, Enum):
    ALL = "ALL"
    DETAIL = "DETAIL"
    FEDERATION = "FEDERATION"
    FUTURE = "FUTURE"
    LOCAL = "LOCAL"
    MIXED = "MIXED"
    SIBLING = "SIBLING"

    def __str__(self) -> str:
        return str(self.value)
