"""
Data Display & Metrics Verification Test Suite.
Validates the rendering, formatting, and live synchronization of dashboard metrics.
"""

import pytest
from framework.pages.login_page import LoginPage
from framework.pages.dashboard_page import DashboardPage
from framework.pages.posts_page import PostsPage
from framework.data.test_data import VALID_USER, SAMPLE_POSTS


@pytest.mark.functional
@pytest.mark.metrics
class TestDataDisplay:

    @pytest.fixture(autouse=True)
    def setup(self, page, reset_db):
        login_page = LoginPage(page).open()
        login_page.login(VALID_USER["username"], VALID_USER["password"])
        self.dashboard_page = DashboardPage(page)
        self.posts_page = PostsPage(page)

    def test_metrics_cards_display_and_formatting(self, page):
        """TC_METRIC_01: Verify all 4 primary metric cards are visible with valid values."""
        assert self.dashboard_page.are_metrics_cards_displayed()

        followers = self.dashboard_page.get_followers_count()
        assert followers != ""
        # Check formatted number contains digits
        assert any(char.isdigit() for char in followers)

        impressions = self.dashboard_page.get_impressions_count()
        assert any(char.isdigit() for char in impressions)

        engagement = self.dashboard_page.get_engagement_rate()
        assert "%" in engagement

    def test_post_metric_synchronizes_with_feed(self, page):
        """TC_METRIC_02: Creating a new post updates the Published Posts metric counter."""
        initial_posts_metric = self.dashboard_page.get_posts_metric_count()
        sample = SAMPLE_POSTS["standard_post"]

        self.posts_page.create_post(sample["platform"], sample["content"])

        updated_posts_metric = self.dashboard_page.get_posts_metric_count()
        assert updated_posts_metric == initial_posts_metric + 1

    def test_post_metric_decrements_on_delete(self, page):
        """TC_METRIC_03: Deleting a post updates the Published Posts metric counter."""
        initial_posts_metric = self.dashboard_page.get_posts_metric_count()

        self.posts_page.delete_latest_post()

        updated_posts_metric = self.dashboard_page.get_posts_metric_count()
        assert updated_posts_metric == initial_posts_metric - 1
