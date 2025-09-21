from enum import Enum


class V0043JobInfoSharedItem(str, Enum):
    MCS = "mcs"
    NONE = "none"
    OVERSUBSCRIBE = "oversubscribe"
    TOPO = "topo"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
