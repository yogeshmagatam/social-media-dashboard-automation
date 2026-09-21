"""
SQL Database Verification Test Suite.
Verifies that all frontend user actions performed via Playwright are accurately
and atomically persisted into the backend SQLite database tables.
"""

import pytest
from framework.pages.login_page import LoginPage
from framework.pages.posts_page import PostsPage
from framework.pages.dashboard_page import DashboardPage
from framework.data.test_data import VALID_USER, SAMPLE_POSTS


@pytest.mark.db
@pytest.mark.regression
class TestSQLDatabaseVerification:

    @pytest.fixture(autouse=True)
    def setup(self, page, reset_db, db_helper):
        self.db = db_helper
        self.login_page = LoginPage(page).open()
        self.login_page.login(VALID_USER["username"], VALID_USER["password"])
        self.posts_page = PostsPage(page)
        self.dashboard_page = DashboardPage(page)

    def test_sql_verify_login_audit_record(self, page):
        """TC_SQL_01: Verify successful UI login produces an audit_log record in the database."""
        user_record = self.db.get_user(VALID_USER["username"])
        assert user_record is not None, "User record not found in users table via SQL."

        user_id = user_record["id"]
        latest_audit = self.db.get_latest_audit_log(action="USER_LOGIN")
        assert latest_audit is not None, "Login action was not recorded in SQL audit_logs."
        assert latest_audit["user_id"] == user_id
        assert VALID_USER["username"] in latest_audit["details"]

    def test_sql_verify_post_creation_in_database(self, page):
        """TC_SQL_02: Verify new post created in UI is committed with correct schema to posts table."""
        sample = SAMPLE_POSTS["linkedin_article"]
        initial_db_count = self.db.get_post_count(username=VALID_USER["username"])

        # Create post through UI
        self.posts_page.create_post(sample["platform"], sample["content"])

        # Verify through direct SQL query
        new_db_count = self.db.get_post_count(username=VALID_USER["username"])
        assert new_db_count == initial_db_count + 1, "SQL post count did not increase by 1."

        latest_post = self.db.get_latest_post_by_user(VALID_USER["username"])
        assert latest_post is not None, "Failed to retrieve newly created post via SQL."
        assert latest_post["content"] == sample["content"]
        assert latest_post["platform"] == sample["platform"]
        assert latest_post["status"] == "published"
        assert latest_post["likes_count"] == 0

        # Verify audit log for post creation
        audit_log = self.db.get_latest_audit_log(action="POST_CREATED")
        assert audit_log is not None
        assert f"#{latest_post['id']}" in audit_log["details"]

    def test_sql_verify_like_increment_in_database(self, page):
        """TC_SQL_03: Verify liking a post via UI updates likes_count column in SQL."""
        post_id = int(self.posts_page.get_first_post_id())
        post_before = self.db.get_post_by_id(post_id)
        db_likes_before = post_before["likes_count"]

        # Like through UI
        ui_likes = self.posts_page.like_latest_post()

        # Query updated state from DB
        post_after = self.db.get_post_by_id(post_id)
        assert post_after["likes_count"] == db_likes_before + 1
        assert post_after["likes_count"] == ui_likes, "UI like count and SQL database count do not match."

    def test_sql_verify_post_deletion_in_database(self, page):
        """TC_SQL_04: Verify deleting a post removes the row from the database and logs an audit."""
        post_id = int(self.posts_page.get_first_post_id())

        # Delete post via UI
        self.posts_page.delete_latest_post()

        # Verify via SQL that the post row is deleted
        deleted_post_row = self.db.get_post_by_id(post_id)
        assert deleted_post_row is None, f"Post with id {post_id} still exists in SQL database after deletion."

        # Verify audit record for deletion
        delete_audit = self.db.get_latest_audit_log(action="POST_DELETED")
        assert delete_audit is not None
        assert f"#{post_id}" in delete_audit["details"]

    def test_sql_and_ui_feed_consistency(self, page):
        """TC_SQL_05: Verify UI feed card count matches total rows in SQL posts table."""
        sql_count = self.db.get_post_count()
        ui_count = self.posts_page.get_feed_posts_count()

        assert sql_count == ui_count, f"Data disparity: SQL reported {sql_count} rows, UI displayed {ui_count} cards."
