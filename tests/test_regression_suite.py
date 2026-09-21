"""
End-to-End Regression Suite.
Runs an integrated user journey covering authentication, navigation, post lifecycle,
real-time metrics, SQL persistence, and session termination prior to release.
"""

import pytest
from framework.pages.login_page import LoginPage
from framework.pages.dashboard_page import DashboardPage
from framework.pages.posts_page import PostsPage
from framework.pages.navigation_page import NavigationPage
from framework.data.test_data import VALID_USER, SAMPLE_POSTS


@pytest.mark.regression
class TestEndToEndRegression:

    def test_full_social_media_lifecycle_e2e(self, page, reset_db, db_helper):
        """
        E2E_REG_01: Complete user workflow:
        1. Negative login attempt & verification
        2. Positive authentication
        3. Dashboard metrics audit
        4. Cross-page navigation
        5. Post creation with multi-channel tag
        6. Direct SQL database confirmation
        7. Feed interaction (Like post) & DB verification
        8. Post deletion & SQL row cleanup
        9. Session logout & route protection
        """
        # --- Step 1: Negative Authentication Verification ---
        login_page = LoginPage(page).open()
        login_page.login(VALID_USER["username"], "IncorrectPassword#123")
        assert login_page.is_error_displayed()

        # --- Step 2: Positive Authentication ---
        login_page.login(VALID_USER["username"], VALID_USER["password"])
        dashboard_page = DashboardPage(page)
        assert dashboard_page.is_loaded()
        assert "dashboard" in page.url.lower()

        # --- Step 3: Metrics Audit ---
        assert dashboard_page.are_metrics_cards_displayed()
        followers_metric = dashboard_page.get_followers_count()
        assert followers_metric != ""

        # Verify initial DB state
        user_record = db_helper.get_user(VALID_USER["username"])
        assert user_record["username"] == VALID_USER["username"]

        # --- Step 4: Multi-tab Navigation ---
        nav_page = NavigationPage(page)
        nav_page.navigate_to_analytics()
        assert "analytics" in page.url.lower()

        nav_page.navigate_to_settings()
        assert "settings" in page.url.lower()

        nav_page.navigate_to_dashboard()
        assert "dashboard" in page.url.lower()

        # --- Step 5: Post Creation ---
        posts_page = PostsPage(page)
        sample = SAMPLE_POSTS["youtube_update"]
        initial_feed_count = posts_page.get_feed_posts_count()

        posts_page.create_post(sample["platform"], sample["content"])
        assert posts_page.get_feed_posts_count() == initial_feed_count + 1
        assert sample["content"] in posts_page.get_latest_post_content()

        # --- Step 6: SQL Verification of Created Post ---
        db_post = db_helper.get_latest_post_by_user(VALID_USER["username"])
        assert db_post is not None
        assert db_post["content"] == sample["content"]
        assert db_post["platform"] == sample["platform"]
        created_post_id = db_post["id"]

        # --- Step 7: Feed Interaction (Like Post) ---
        new_likes = posts_page.like_latest_post()
        assert new_likes > 0

        # Assert in SQL
        db_post_liked = db_helper.get_post_by_id(created_post_id)
        assert db_post_liked["likes_count"] == new_likes

        # --- Step 8: Post Deletion & SQL Cleanup ---
        posts_page.delete_latest_post()
        assert posts_page.get_feed_posts_count() == initial_feed_count

        # Verify SQL row deleted
        db_post_deleted = db_helper.get_post_by_id(created_post_id)
        assert db_post_deleted is None

        # Verify deletion audit log
        del_audit = db_helper.get_latest_audit_log(action="POST_DELETED")
        assert f"#{created_post_id}" in del_audit["details"]

        # --- Step 9: Session Logout & Route Security ---
        nav_page.logout()
        assert login_page.is_loaded()

        # Direct protected URL check
        page.goto(f"{login_page.base_url}/dashboard")
        assert "login" in page.url.lower()
