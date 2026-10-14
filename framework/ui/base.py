"""Small helpers shared by page objects. The app has no test ids and its labels are not tied to inputs,
so fields are found through the label text inside the same block."""

import re
from playwright.sync_api import Locator, Page


def field(page: Page, label: str) -> Locator:
    """The block of a form field (label + control), found by the label text."""
    return page.locator("div.relative.w-full.text-left").filter(has=page.locator("label", has_text=label)).first


def pick(page: Page, field_block: Locator, text: str) -> None:
    """Choose an option in the app's dropdowns. Searchable ones (customer) get the text typed to filter the list;
    the others (invoice) just open on click. Options are plain <li> without roles."""
    search_box = field_block.locator("input[type='text']")
    if search_box.count():
        search_box.first.click()
        search_box.first.press_sequentially(text, delay=20)  # typing (not fill) makes the app search as it does for a person
    else:
        field_block.locator("div[tabindex]").first.click()
    page.locator("li").filter(has_text=text).first.click()


def entity_id(page: Page) -> int:
    """Id of the entity whose page we are on: the app opens /admin/<area>/<id>/view after saving."""
    match = re.search(r"/(\d+)/view$", page.url)
    assert match, f"Not on an entity page: {page.url}"
    return int(match.group(1))
