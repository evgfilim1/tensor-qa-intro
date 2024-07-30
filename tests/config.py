import os
from dataclasses import dataclass
from typing import Self, Literal


@dataclass(kw_only=True)
class Config:
    downloads_dir: Literal["{tempdir}"] | str
    selenium_hub_url: str
    current_region_substr: str
    default_wait_timeout: int
    record_videos: bool

    @classmethod
    def from_env(cls) -> Self:
        env = os.getenv
        return cls(
            downloads_dir=env("DOWNLOADS_DIR"),
            selenium_hub_url=env("SELENIUM_HUB_URL"),
            current_region_substr=env("CURRENT_REGION_SUBSTR"),
            default_wait_timeout=int(env("DEFAULT_WAIT_TIMEOUT")),
            record_videos=env("RECORD_VIDEOS", "").lower() not in {"0", "false", ""},
        )
