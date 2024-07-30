import logging

import pytest
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.remote.webdriver import WebDriver

from .config import Config
from .pages.sbis import HomePage as SBISHomePage

_log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def config() -> Config:
    return Config.from_env()


@pytest.fixture(scope="function")
def driver(config: Config, request: pytest.FixtureRequest) -> WebDriver:
    options = ArgOptions()
    options.set_capability("browserName", "firefox")
    options.set_capability("se:recordVideo", config.record_videos)
    options.set_capability("se:timeZone", "Asia/Yekaterinburg")
    options.set_capability("se:name", request.node.name)

    with WebDriver(command_executor=config.selenium_hub_url, options=options) as driver:
        _log.info("Opened session %s for test %s", driver.session_id, request.node.name)
        yield driver


@pytest.fixture(scope="function", autouse=True)
def enable_all_tests_logs(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG, logger="tests")


@pytest.fixture(scope="function")
def sbis_homepage(driver: WebDriver) -> SBISHomePage:
    return SBISHomePage.navigate_and_init(driver)
