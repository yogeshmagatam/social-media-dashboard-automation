"""
Base Page Object for Playwright Automation.
Encapsulates common browser actions, waits, and assertions.
"""

from playwright.sync_api import Page, expect
from framework.config.config import BASE_URL, DEFAULT_TIMEOUT, SCREENSHOTS_DIR
from framework.utils.logger import get_logger

logger = get_logger("BasePage")


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = BASE_URL
        self.timeout = DEFAULT_TIMEOUT

    def navigate_to(self, path: str = ""):
        """Navigates to a specific path relative to base_url."""
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        logger.info(f"Navigating to {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)

    def click(self, selector: str, timeout: int = None):
        """Clicks an element with auto-wait."""
        t = timeout or self.timeout
        logger.info(f"Clicking element: {selector}")
        self.page.wait_for_selector(selector, state="visible", timeout=t)
        self.page.click(selector, timeout=t)

    def fill(self, selector: str, text: str, timeout: int = None):
        """Fills an input element with text."""
        t = timeout or self.timeout
        logger.info(f"Filling element {selector} with text length: {len(text)}")
        self.page.wait_for_selector(selector, state="visible", timeout=t)
        self.page.fill(selector, text, timeout=t)

    def get_text(self, selector: str, timeout: int = None) -> str:
        """Retrieves inner text of an element."""
        t = timeout or self.timeout
        self.page.wait_for_selector(selector, state="visible", timeout=t)
        return self.page.inner_text(selector, timeout=t).strip()

    def get_value(self, selector: str) -> str:
        """Retrieves input value."""
        return self.page.input_value(selector)

    def is_visible(self, selector: str, timeout: int = 3000) -> bool:
        """Checks if element is visible within timeout."""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def select_option(self, selector: str, value: str):
        """Selects option in a dropdown element."""
        logger.info(f"Selecting option '{value}' in {selector}")
        self.page.wait_for_selector(selector, state="visible", timeout=self.timeout)
        self.page.select_option(selector, value=value)

    def take_screenshot(self, name: str) -> str:
        """Captures page screenshot saved to reports/screenshots."""
        file_path = SCREENSHOTS_DIR / f"{name}.png"
        self.page.screenshot(path=str(file_path), full_page=True)
        logger.info(f"Screenshot saved to: {file_path}")
        return str(file_path)

    def get_current_url(self) -> str:
        return self.page.url

    def get_title(self) -> str:
        return self.page.title()
