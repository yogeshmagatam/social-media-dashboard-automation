"""
Navigation Test Suite.
Validates sidebar routing, active tab highlighting, and view switching.
"""

import pytest
from framework.pages.login_page import LoginPage
from framework.pages.navigation_page import NavigationPage
from framework.data.test_data import VALID_USER


@pytest.mark.smoke
@pytest.mark.navigation
class TestNavigation:

    @pytest.fixture(autouse=True)
    def setup_authenticated_session(self, page):
        """Authenticates before each navigation test."""
        login_page = LoginPage(page).open()
        login_page.login(VALID_USER["username"], VALID_USER["password"])
        self.nav = NavigationPage(page)

    def test_navigate_to_post_manager(self, page):
        """TC_NAV_01: Verify navigation to Post Manager view."""
        self.nav.navigate_to_posts()
        assert "posts" in page.url.lower()
        heading = self.nav.get_page_heading()
        assert "Post Management" in heading
        assert self.nav.is_nav_item_active(self.nav.NAV_POSTS)

    def test_navigate_to_analytics(self, page):
        """TC_NAV_02: Verify navigation to Analytics view."""
        self.nav.navigate_to_analytics()
        assert "analytics" in page.url.lower()
        heading = self.nav.get_page_heading()
        assert "Analytics" in heading
        assert self.nav.is_nav_item_active(self.nav.NAV_ANALYTICS)
        # Check channel distribution section exists
        assert page.locator("#analytics-view").is_visible()

    def test_navigate_to_settings(self, page):
        """TC_NAV_03: Verify navigation to Settings view."""
        self.nav.navigate_to_settings()
        assert "settings" in page.url.lower()
        heading = self.nav.get_page_heading()
        assert "Configuration" in heading
        assert self.nav.is_nav_item_active(self.nav.NAV_SETTINGS)
        # Check profile username is visible in settings
        assert page.locator("#profile-username").inner_text() == VALID_USER["username"]

    def test_return_to_dashboard(self, page):
        """TC_NAV_04: Verify navigating back to Dashboard."""
        self.nav.navigate_to_settings()
        self.nav.navigate_to_dashboard()
        assert "dashboard" in page.url.lower()
        heading = self.nav.get_page_heading()
        assert "Overview" in heading
        assert self.nav.is_nav_item_active(self.nav.NAV_DASHBOARD)
