"""
Page Object Model for Application Navigation & Header Controls.
"""

from playwright.sync_api import Page
from framework.pages.base_page import BasePage
from framework.utils.logger import get_logger

logger = get_logger("NavigationPage")


class NavigationPage(BasePage):
    NAV_DASHBOARD = "#nav-dashboard"
    NAV_POSTS = "#nav-posts"
    NAV_ANALYTICS = "#nav-analytics"
    NAV_SETTINGS = "#nav-settings"
    LOGOUT_BTN = "#logout-btn"
    PAGE_TITLE = "#page-title"
    SIDEBAR = "#main-sidebar"

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_dashboard(self):
        self.click(self.NAV_DASHBOARD)
        self.page.wait_for_selector(self.PAGE_TITLE, state="visible")

    def navigate_to_posts(self):
        self.click(self.NAV_POSTS)
        self.page.wait_for_selector(self.PAGE_TITLE, state="visible")

    def navigate_to_analytics(self):
        self.click(self.NAV_ANALYTICS)
        self.page.wait_for_selector(self.PAGE_TITLE, state="visible")

    def navigate_to_settings(self):
        self.click(self.NAV_SETTINGS)
        self.page.wait_for_selector(self.PAGE_TITLE, state="visible")

    def logout(self):
        logger.info("Logging out from application")
        self.click(self.LOGOUT_BTN)
        self.page.wait_for_selector("#username", state="visible")

    def get_page_heading(self) -> str:
        return self.get_text(self.PAGE_TITLE)

    def is_nav_item_active(self, selector: str) -> bool:
        classes = self.page.locator(selector).get_attribute("class") or ""
        return "active" in classes
