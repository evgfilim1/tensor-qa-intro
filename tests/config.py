import os
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Literal, overload, NewType, cast

_Required = NewType("_Required", object)
_required = _Required(object())


@overload
def env(key: str, default: _Required = _required) -> str: ...


@overload
def env(key: str, default: str) -> str: ...


@overload
def env(key: str, default: None) -> str | None: ...


def env(key: str, default: str | _Required | None = _required) -> str | None:
    value = os.getenv(key, None)
    if value is None and default is _required:
        raise ValueError(f"Required environment variable {key!r} is not set")
    return value if value is not None else default


@dataclass(kw_only=True)
class Config:
    downloads_dir: Literal["{tempdir}"] | Path
    selenium_hub_url: str
    current_region_substr: str
    default_wait_timeout: int
    record_videos: bool

    @classmethod
    def from_env(cls) -> Self:
        downloads_dir_raw = env("DOWNLOADS_DIR", "{tempdir}")
        downloads_dir: Literal["{tempdir}"] | Path
        if downloads_dir_raw == "{tempdir}":
            downloads_dir = cast(Literal["{tempdir}"], downloads_dir_raw)
        else:
            downloads_dir = Path(downloads_dir_raw)
        return cls(
            downloads_dir=downloads_dir,
            selenium_hub_url=env("SELENIUM_HUB_URL"),
            current_region_substr=env("CURRENT_REGION_SUBSTR"),
            default_wait_timeout=int(env("DEFAULT_WAIT_TIMEOUT", "15")),
            record_videos=env("RECORD_VIDEOS", "").lower() not in {"0", "false", ""},
        )
