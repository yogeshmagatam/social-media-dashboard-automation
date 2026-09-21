"""
Page Object Model for the Authentication / Login Page.
"""

from playwright.sync_api import Page
from framework.pages.base_page import BasePage
from framework.utils.logger import get_logger

logger = get_logger("LoginPage")


class LoginPage(BasePage):
    # Locators
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-btn"
    ERROR_BANNER = "#error-banner"
    ERROR_MESSAGE = "#error-message"
    BRAND_TITLE = ".brand-title"
    REMEMBER_ME = "#remember-me"

    def __init__(self, page: Page):
        super().__init__(page)

    def open(self):
        """Navigates to the login page."""
        self.navigate_to("login")
        return self

    def is_loaded(self) -> bool:
        """Verifies login page elements are displayed."""
        return (
            self.is_visible(self.USERNAME_INPUT) and
            self.is_visible(self.PASSWORD_INPUT) and
            self.is_visible(self.LOGIN_BUTTON)
        )

    def login(self, username: str, password: str):
        """Fills login form and submits."""
        logger.info(f"Attempting login for username: '{username}'")
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self) -> str:
        """Returns displayed validation or authentication error message."""
        if self.is_visible(self.ERROR_MESSAGE, timeout=4000):
            return self.get_text(self.ERROR_MESSAGE)
        return ""

    def is_error_displayed(self) -> bool:
        """Checks if the error banner is currently visible."""
        return self.is_visible(self.ERROR_BANNER, timeout=3000)
