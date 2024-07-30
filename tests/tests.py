from pathlib import Path

import pytest
import requests

from .config import Config
from .pages.base import WarnMode
from .pages.sbis import HomePage as SBISHomePage

OTHER_REGION_SUBSTR = "Камчатский край"
MiB = 1024 * 1024


def test_scenario1(sbis_homepage: SBISHomePage) -> None:
    contacts_page = sbis_homepage.navigate_to_contacts()
    contacts_page.wait_page_loaded()
    tensor_page = contacts_page.click_on_tensor_logo()
    tensor_page.wait_page_loaded()

    tensor_page.check_driver_url(warn_mode=WarnMode.ERROR)

    tensor_page.get_strength_in_people_block()  # fails with exception if not found
    about_page = tensor_page.navigate_to_about_people()
    about_page.wait_page_loaded()

    about_page.check_driver_url(warn_mode=WarnMode.ERROR)

    image_sizes = about_page.get_working_images_sizes()

    assert all(
        img.width == image_sizes[0].width and img.height == image_sizes[0].height
        for img in image_sizes
    )


def test_scenario2(sbis_homepage: SBISHomePage, config: Config) -> None:
    contacts = sbis_homepage.navigate_to_contacts()
    contacts.wait_page_loaded()

    assert config.current_region_substr in contacts.get_selected_region()
    assert config.current_region_substr in contacts.title

    partners = contacts.get_partners_list()
    url = sbis_homepage.url
    contacts.choose_other_region(OTHER_REGION_SUBSTR)

    assert OTHER_REGION_SUBSTR in contacts.get_selected_region()
    assert OTHER_REGION_SUBSTR in contacts.title
    assert partners != contacts.get_partners_list()
    assert url != sbis_homepage.url


def test_scenario3(sbis_homepage: SBISHomePage, config: Config, tmp_path: Path) -> None:
    downloads = sbis_homepage.navigate_to_download_local()
    downloads.wait_page_loaded()
    downloads.open_plugin_tab()
    download_info = downloads.get_download_info()
    if config.downloads_dir == "{tempdir}":
        download_dir = tmp_path
    else:
        download_dir = config.downloads_dir
    plugin_path = download_dir / f"plugin.{download_info.extension}"
    # if plugin_path already exists, opening in "wb" mode will truncate it
    with requests.get(download_info.url, stream=True) as dl, plugin_path.open("wb") as f:
        dl.raise_for_status()
        for chunk in dl.iter_content(chunk_size=None):
            f.write(chunk)

    # The reported plugin size (in MiB) is rounded to 2 decimal places, so allow a small tolerance
    tolerance = 0.01
    assert abs(plugin_path.stat().st_size / MiB - download_info.size_mib) < tolerance
