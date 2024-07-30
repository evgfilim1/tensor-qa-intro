from typing import NamedTuple, ParamSpec, TypeVar

PS = ParamSpec("PS")
RT = TypeVar("RT")


class DownloadInfo(NamedTuple):
    url: str
    extension: str
    size_mib: float


class Size(NamedTuple):
    height: int
    width: int


class WrongPageWarning(RuntimeWarning):
    pass
