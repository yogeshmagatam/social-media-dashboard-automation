"""
Page Object Model for the Dashboard View & Metrics Display.
"""

from playwright.sync_api import Page
from framework.pages.base_page import BasePage
from framework.utils.logger import get_logger

logger = get_logger("DashboardPage")


class DashboardPage(BasePage):
    # Metric Locators
    METRIC_FOLLOWERS = "#metric-followers"
    METRIC_IMPRESSIONS = "#metric-impressions"
    METRIC_ENGAGEMENT = "#metric-engagement"
    METRIC_POSTS = "#metric-posts"
    
    CARD_FOLLOWERS = "#card-followers"
    CARD_IMPRESSIONS = "#card-impressions"
    CARD_ENGAGEMENT = "#card-engagement"
    CARD_POSTS = "#card-posts"
    
    PAGE_TITLE = "#page-title"
    LOGGED_IN_NAME = "#logged-in-user-name"
    LOGGED_IN_ROLE = "#logged-in-user-role"

    def __init__(self, page: Page):
        super().__init__(page)

    def is_loaded(self) -> bool:
        """Verifies dashboard elements are rendered."""
        return self.is_visible(self.PAGE_TITLE) and self.is_visible(self.METRIC_FOLLOWERS)

    def get_followers_count(self) -> str:
        return self.get_text(self.METRIC_FOLLOWERS)

    def get_impressions_count(self) -> str:
        return self.get_text(self.METRIC_IMPRESSIONS)

    def get_engagement_rate(self) -> str:
        return self.get_text(self.METRIC_ENGAGEMENT)

    def get_posts_metric_count(self) -> int:
        text = self.get_text(self.METRIC_POSTS)
        return int(text.replace(",", ""))

    def are_metrics_cards_displayed(self) -> bool:
        return (
            self.is_visible(self.CARD_FOLLOWERS) and
            self.is_visible(self.CARD_IMPRESSIONS) and
            self.is_visible(self.CARD_ENGAGEMENT) and
            self.is_visible(self.CARD_POSTS)
        )

    def get_user_profile_info(self) -> dict:
        return {
            "name": self.get_text(self.LOGGED_IN_NAME),
            "role": self.get_text(self.LOGGED_IN_ROLE)
        }
