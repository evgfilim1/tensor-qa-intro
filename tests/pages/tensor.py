from __future__ import annotations

import logging
from typing import Final

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .base import BasePage, Selector, WarnMode
from .utils import Size

_call_log = logging.getLogger(__name__)


# page_url = https://tensor.ru
class HomePage(BasePage):
    ROOT_URL: Final[str] = "https://tensor.ru/"

    STRENGTH_IN_PEOPLE_SELECTOR: Final[Selector] = (
        By.XPATH,
        # language=xpath
        "//div[contains(@class, 'tensor_ru-Index__card') and ./p[contains(., 'Сила в людях')]]",
    )
    ABOUT_PEOPLE_SELECTOR: Final[Selector] = (
        By.XPATH,
        # language=xpath
        "//div[contains(@class, 'tensor_ru-Index__card') and ./p[contains(., 'Сила в людях')]]"
        "//a[contains(., 'Подробнее')]",
    )
    CLOSE_COOKIE_AGREEMENT_SELECTOR: Final[Selector] = (
        By.CSS_SELECTOR,
        ".tensor_ru-CookieAgreement__close",
    )

    def __init__(self, driver, *, warn_mode: WarnMode = WarnMode.DEFAULT) -> None:
        super().__init__(driver, warn_mode=warn_mode)

    def _maybe_close_cookie_agreement(self) -> None:
        try:
            self._click_element(self.CLOSE_COOKIE_AGREEMENT_SELECTOR)
            self._log(logging.DEBUG, "Closed cookie agreement")
        except NoSuchElementException:
            self._log(logging.DEBUG, "Cookie agreement wasn't found")

    def get_strength_in_people_block(self) -> WebElement:
        return self._driver.find_element(*self.STRENGTH_IN_PEOPLE_SELECTOR)

    def navigate_to_about_people(self) -> AboutPeoplePage:
        self._maybe_close_cookie_agreement()
        self._click_element(self.ABOUT_PEOPLE_SELECTOR)
        return AboutPeoplePage(self._driver)


# page_url = https://tensor.ru/about
class AboutPeoplePage(BasePage):
    ROOT_URL: Final[str] = "https://tensor.ru/about"

    WORKING_IMAGES_SELECTOR: Final[Selector] = (
        By.XPATH,
        # language=xpath
        "//div[contains(@class, 'tensor_ru-container') and .//h2[contains(., 'Работаем')]]"
        "/div[@class='s-Grid-container']//img",
    )

    def get_working_images_sizes(self) -> list[Size]:
        return [
            Size(
                height=img.size["height"],
                width=img.size["width"],
            )
            for img in self._driver.find_elements(*self.WORKING_IMAGES_SELECTOR)
        ]
