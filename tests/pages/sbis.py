from __future__ import annotations

import logging
import re
from typing import Final

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

from . import tensor
from .base import BasePage, Selector
from .utils import DownloadInfo

_call_log = logging.getLogger(__name__)


# page_url = https://sbis.ru
class HomePage(BasePage):
    ROOT_URL: Final[str] = "https://sbis.ru/"

    CONTACTS_SELECTOR: Final[Selector] = (
        By.XPATH,
        # language=xpath
        "//ul[contains(@class, 'sbisru-Header__menu')]//a[. = 'Контакты']",
    )
    DOWNLOAD_LOCAL_SELECTOR: Final[Selector] = (
        By.XPATH,
        # language=xpath
        "//a[@class='sbisru-Footer__link' and starts-with(., 'Скачать')]",
    )

    def navigate_to_contacts(self) -> ContactsPage:
        self._click_element(self.CONTACTS_SELECTOR)
        return ContactsPage(self._driver)

    def navigate_to_download_local(self) -> DownloadPluginPage:
        self._click_element(self.DOWNLOAD_LOCAL_SELECTOR)
        return DownloadPluginPage(self._driver)


# page_url = https://sbis.ru/contacts
class ContactsPage(BasePage):
    ROOT_URL: Final[str] = "https://sbis.ru/contacts"

    TENSOR_LOGO_SELECTOR: Final[Selector] = (
        By.CSS_SELECTOR,
        "#contacts_clients a.sbisru-Contacts__logo-tensor",
    )
    REGION_CHOOSER_SELECTOR: Final[Selector] = (
        By.CSS_SELECTOR,
        "span.sbis_ru-Region-Chooser__text",
    )
    REGION_LINKS_SELECTOR: Final[Selector] = (
        By.XPATH,
        # language=xpath
        "//div[contains(@class, 'sbis_ru-Region-Panel')]"
        "//li[contains(@class, 'sbis_ru-Region-Panel__item')]/span/span",
    )
    PARTNERS_SELECTOR: Final[Selector] = (
        By.XPATH,
        # language=xpath
        "//div[contains(@class, 'sbisru-Contacts-List__col')]"
        "//div[contains(@class, 'sbisru-Contacts-List__name')]",
    )

    def click_on_tensor_logo(self) -> tensor.HomePage:
        self._click_element(self.TENSOR_LOGO_SELECTOR)
        self._switch_to_new_window()
        return tensor.HomePage(self._driver)

    def get_selected_region(self) -> str:
        return self._driver.find_element(*self.REGION_CHOOSER_SELECTOR).text

    def choose_other_region(self, region_substr: str) -> None:
        old_partner = self._driver.find_element(*self.PARTNERS_SELECTOR)
        self._click_element(self.REGION_CHOOSER_SELECTOR)
        self._wait_until(
            expected_conditions.visibility_of_any_elements_located(self.REGION_LINKS_SELECTOR),
        )
        for el in self._driver.find_elements(*self.REGION_LINKS_SELECTOR):
            if region_substr in el.text:
                el.click()
                break
        self._wait_until_not(
            expected_conditions.visibility_of_all_elements_located(self.REGION_LINKS_SELECTOR),
        )
        # wait until partner list refreshes
        self._wait_until(expected_conditions.staleness_of(old_partner))

    def get_partners_list(self) -> list[str]:
        return [el.text for el in self._driver.find_elements(*self.PARTNERS_SELECTOR)]


# page_url = https://sbis.ru/download
class DownloadPluginPage(BasePage):
    ROOT_URL: Final[str] = "https://sbis.ru/download"

    PLUGIN_SELECTOR: Final[Selector] = (
        By.XPATH,
        # language=xpath
        "//div[contains(@class, 'controls-TabButton__right-align')"
        " and .//div[@class='controls-TabButton__caption' and contains(., 'Плагин')]]",
    )
    DOWNLOAD_WEB_INSTALLER_SELECTOR: Final[Selector] = (
        By.XPATH,
        # language=xpath
        "//div[contains(@class, 'sbis_ru-DownloadNew-block')"
        " and .//h3[starts-with(., 'Веб-установщик')]]"
        "//a[contains(@class, 'sbis_ru-DownloadNew-loadLink__link')]",
    )
    DOWNLOAD_BUTTON_REGEXP: Final[re.Pattern[str]] = re.compile(
        r"Скачать \((Exe|Msi) (\d+\.\d+) МБ\)",
    )

    def open_plugin_tab(self) -> None:
        self._click_element(self.PLUGIN_SELECTOR)

    def get_download_info(self) -> DownloadInfo:
        el = self._driver.find_element(*self.DOWNLOAD_WEB_INSTALLER_SELECTOR)
        m = self.DOWNLOAD_BUTTON_REGEXP.match(el.text)
        if m is None:
            raise ValueError("Could not extract download size")
        url = el.get_attribute("href")
        if url is None:
            raise ValueError("Could not extract download URL")
        return DownloadInfo(
            url=url,
            extension=m[1].lower(),
            size_mib=float(m[2]),
        )
