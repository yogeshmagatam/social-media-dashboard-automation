"""
Authentication Test Suite (Positive & Negative Test Cases).
Validates user authentication, error states, and session lifecycles.
"""

import pytest
from framework.pages.login_page import LoginPage
from framework.pages.dashboard_page import DashboardPage
from framework.pages.navigation_page import NavigationPage
from framework.data.test_data import VALID_USER, ADMIN_USER, NEGATIVE_LOGIN_CASES


@pytest.mark.smoke
@pytest.mark.auth
class TestAuthentication:

    def test_valid_user_login(self, page):
        """TC_AUTH_POS_01: Valid user should successfully authenticate and reach dashboard."""
        login_page = LoginPage(page).open()
        assert login_page.is_loaded(), "Login page failed to load correctly."

        login_page.login(VALID_USER["username"], VALID_USER["password"])

        dashboard_page = DashboardPage(page)
        assert dashboard_page.is_loaded(), "Dashboard failed to load after valid login."
        assert "dashboard" in page.url.lower()

        profile = dashboard_page.get_user_profile_info()
        assert VALID_USER["full_name"] in profile["name"]

    def test_admin_user_login(self, page):
        """TC_AUTH_POS_02: Admin user login verification."""
        login_page = LoginPage(page).open()
        login_page.login(ADMIN_USER["username"], ADMIN_USER["password"])

        dashboard_page = DashboardPage(page)
        assert dashboard_page.is_loaded()
        profile = dashboard_page.get_user_profile_info()
        assert "admin" in profile["role"].lower()

    @pytest.mark.parametrize("case", NEGATIVE_LOGIN_CASES, ids=[c["desc"] for c in NEGATIVE_LOGIN_CASES])
    def test_negative_login_scenarios(self, page, case):
        """TC_AUTH_NEG_01..03: Invalid credentials and SQL injection attempts must be rejected."""
        login_page = LoginPage(page).open()
        login_page.login(case["username"], case["password"])

        assert login_page.is_error_displayed(), f"Expected error banner for case: {case['desc']}"
        error_text = login_page.get_error_message()
        assert case["expected_error"].lower() in error_text.lower()
        assert "dashboard" not in page.url.lower()

    def test_empty_credentials_submission(self, page):
        """TC_AUTH_NEG_04: Submitting empty form should fail validation."""
        login_page = LoginPage(page).open()
        login_page.login("", "")

        # HTML5 / Server validation check
        assert "dashboard" not in page.url.lower()

    def test_logout_functionality(self, page):
        """TC_AUTH_POS_03: Clicking logout invalidates session and navigates back to login."""
        login_page = LoginPage(page).open()
        login_page.login(VALID_USER["username"], VALID_USER["password"])

        nav_page = NavigationPage(page)
        nav_page.logout()

        # Assert user is on login page
        assert login_page.is_loaded()
        assert "login" in page.url.lower()

        # Attempt to access protected dashboard directly
        page.goto(f"{login_page.base_url}/dashboard")
        assert "login" in page.url.lower()
