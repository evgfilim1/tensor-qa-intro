import logging
import warnings
from abc import ABC
from enum import StrEnum
from typing import Final, Self, Any, Callable
from urllib.parse import urlparse

from selenium.common import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.by import ByType, By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from .utils import WrongPageWarning
from ..config import Config

type Selector = tuple[ByType, str]

WAIT_TIMEOUT: float = Config.from_env().default_wait_timeout

_log = logging.getLogger(__name__.removesuffix(".base"))


class WarnMode(StrEnum):
    IGNORE = "ignore"
    DEFAULT = "default"
    ERROR = "error"


def _page_loaded(driver: WebDriver) -> bool:
    return driver.execute_script("return document.readyState === 'complete'")


class BasePage(ABC):
    ROOT_URL: str

    PRELOAD_OVERLAY_SELECTOR: Final[tuple[ByType, str]] = (
        By.CSS_SELECTOR,
        ".preload-overlay",
    )

    @classmethod
    def navigate_and_init(
        cls,
        driver: WebDriver,
        *,
        warn_mode: WarnMode = WarnMode.DEFAULT,
    ) -> Self:
        driver.get(cls.ROOT_URL)
        return cls(driver, warn_mode=warn_mode)

    def __init__(self, driver: WebDriver, *, warn_mode: WarnMode = WarnMode.DEFAULT) -> None:
        self._driver = driver
        self._log(logging.DEBUG, "Driver is on page %s", self.url)
        self._maybe_warn_driver_url(warn_mode=warn_mode)
        self._known_windows = {self._driver.current_window_handle}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "ROOT_URL"):
            raise TypeError(f"Class {cls.__name__} must define `ROOT_URL` attribute")

    @property
    def url(self) -> str:
        return self._driver.current_url

    @property
    def title(self) -> str:
        return self._driver.title

    def wait_page_loaded(self) -> None:
        self._log(logging.DEBUG, "Waiting for page to be loaded")
        WebDriverWait(self._driver, WAIT_TIMEOUT).until(_page_loaded)

    def check_driver_url(self, *, warn_mode: WarnMode = WarnMode.DEFAULT) -> None:
        self._maybe_warn_driver_url(warn_mode=warn_mode)

    def _maybe_warn_driver_url(self, *, warn_mode: WarnMode = WarnMode.DEFAULT) -> None:
        if warn_mode == WarnMode.IGNORE:
            return
        parsed_url = urlparse(self._driver.current_url)
        parsed_root_url = urlparse(self.ROOT_URL)
        if warn_mode == WarnMode.ERROR:
            warnings.filterwarnings("error", category=WrongPageWarning)
        elif warn_mode == WarnMode.DEFAULT:
            warnings.filterwarnings("default", category=WrongPageWarning)
        else:
            raise ValueError(f"Unknown warn mode: {warn_mode}")
        if parsed_url.netloc != parsed_root_url.netloc:
            warnings.warn(
                f"The driver is on a different domain: expected: {parsed_root_url.netloc},"
                f" actual: {parsed_url.netloc}",
                WrongPageWarning,
                stacklevel=3,
            )
        if parsed_url.path != parsed_root_url.path:
            warnings.warn(
                f"The driver is on a different path: expected: {parsed_root_url.path},"
                f" actual: {parsed_url.path}",
                WrongPageWarning,
                stacklevel=3,
            )

    def _click_element(self, selector: Selector, *, retry_count: int = 2) -> None:
        self._log(
            logging.DEBUG,
            "Waiting for element %s to be clickable",
            selector,
        )
        # Fix `ElementClickInterceptedException`
        self._wait_until(
            expected_conditions.invisibility_of_element_located(self.PRELOAD_OVERLAY_SELECTOR),
        )
        try:
            self._wait_until(expected_conditions.element_to_be_clickable(selector))
            self._driver.find_element(*selector).click()
        except (StaleElementReferenceException, ElementClickInterceptedException) as e:
            if retry_count == 0:
                raise
            retry_count -= 1
            self._log(
                logging.DEBUG,
                "Error occurred when clicking an element %s, retrying (count_left=%d)",
                selector,
                retry_count,
                exc_info=e,
            )
            self._click_element(selector, retry_count=retry_count)
        self._log(logging.DEBUG, "Clicked on element %s", selector)

    def _wait_until(
        self,
        condition: Callable[[WebDriver], Any],
        *,
        timeout: float | None = None,
    ) -> None:
        if timeout is None:
            timeout = WAIT_TIMEOUT
        WebDriverWait(self._driver, timeout).until(condition)

    def _wait_until_not(
        self, condition: Callable[[WebDriver], Any], *, timeout: float | None = None
    ) -> None:
        if timeout is None:
            timeout = WAIT_TIMEOUT
        WebDriverWait(self._driver, timeout).until_not(condition)

    def _switch_to_new_window(self) -> None:
        self._log(logging.DEBUG, "Requested switch to new window")
        for window in self._driver.window_handles:
            if window not in self._known_windows:
                self._log(logging.DEBUG, "Detected new window %s, switching", window)
                self._driver.switch_to.window(window)
                self._driver.execute_script("window.focus();")
                self._known_windows.add(window)
                break

    def _log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None:
        extra = kwargs.pop("extra", {})
        extra.update(
            {
                "page": self.__class__.__name__,
                "url": self.url,
            }
        )
        stacklevel = kwargs.pop("stacklevel", 1)
        stacklevel += 1
        _log.log(level, msg, *args, extra=extra, stacklevel=stacklevel, **kwargs)
