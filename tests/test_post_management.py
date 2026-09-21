"""
Post Management Test Suite.
Validates creating, validating, filtering, liking, and deleting posts.
"""

import time
import pytest
from framework.pages.login_page import LoginPage
from framework.pages.posts_page import PostsPage
from framework.pages.dashboard_page import DashboardPage
from framework.data.test_data import VALID_USER, SAMPLE_POSTS


@pytest.mark.functional
@pytest.mark.posts
class TestPostManagement:

    @pytest.fixture(autouse=True)
    def setup_authenticated_session(self, page, reset_db):
        """Pre-authenticates and initializes fresh seeded DB for each test."""
        login_page = LoginPage(page).open()
        login_page.login(VALID_USER["username"], VALID_USER["password"])
        self.posts_page = PostsPage(page)
        self.dashboard_page = DashboardPage(page)

    def test_create_standard_post(self, page):
        """TC_POST_01: Create and publish a new social media post."""
        initial_count = self.posts_page.get_feed_posts_count()
        sample = SAMPLE_POSTS["standard_post"]

        self.posts_page.create_post(
            platform=sample["platform"],
            content=sample["content"]
        )

        # Assert post count incremented
        updated_count = self.posts_page.get_feed_posts_count()
        assert updated_count == initial_count + 1

        # Assert top post content matches
        latest_content = self.posts_page.get_latest_post_content()
        assert sample["content"] in latest_content

    def test_create_post_with_media(self, page):
        """TC_POST_02: Create a post with an image attachment."""
        sample = SAMPLE_POSTS["instagram_photo"]

        self.posts_page.create_post(
            platform=sample["platform"],
            content=sample["content"],
            media_url=sample["media_url"]
        )

        latest_content = self.posts_page.get_latest_post_content()
        assert sample["content"] in latest_content

        # Verify image element is rendered
        first_card = page.locator(".post-card").first
        img = first_card.locator(".post-media-img")
        assert img.is_visible()
        assert img.get_attribute("src") == sample["media_url"]

    def test_char_counter_updates(self, page):
        """TC_POST_03: Character counter tracks user keystrokes in real time."""
        test_text = "Automation testing with Playwright"
        self.posts_page.fill(self.posts_page.POST_CONTENT_INPUT, test_text)

        counter_text = self.posts_page.get_char_counter_text()
        expected = f"{len(test_text)} / 280"
        assert counter_text == expected

    def test_post_creation_boundary_max_allowed(self, page):
        """TC_POST_04: Max 280 characters post should be accepted."""
        sample = SAMPLE_POSTS["max_boundary_post"]

        self.posts_page.create_post(
            platform=sample["platform"],
            content=sample["content"]
        )

        latest_content = self.posts_page.get_latest_post_content()
        assert len(latest_content) == 280

    def test_empty_post_validation_error(self, page):
        """TC_POST_05: Negative test - empty post should be rejected with validation error."""
        initial_count = self.posts_page.get_feed_posts_count()

        # Try submitting empty content
        self.posts_page.click(self.posts_page.SUBMIT_POST_BTN)

        # Feed post count must remain identical
        current_count = self.posts_page.get_feed_posts_count()
        assert current_count == initial_count

    def test_like_post_increments_counter(self, page):
        """TC_POST_06: Clicking like button updates like counter asynchronously."""
        updated_likes = self.posts_page.like_latest_post()
        assert updated_likes > 0

    def test_delete_post_removes_from_feed(self, page):
        """TC_POST_07: Deleting a post removes it from the UI feed."""
        initial_count = self.posts_page.get_feed_posts_count()
        post_id = self.posts_page.get_first_post_id()

        self.posts_page.delete_latest_post()

        # Check post is removed
        assert not page.locator(f"#post-{post_id}").is_visible()
        new_count = self.posts_page.get_feed_posts_count()
        assert new_count == initial_count - 1

    def test_filter_feed_by_platform(self, page):
        """TC_POST_08: Selecting a platform in filter dropdown narrows displayed posts."""
        self.posts_page.filter_by_platform("Twitter/X")

        visible_cards = page.locator(".post-card:visible")
        count = visible_cards.count()
        assert count > 0

        # Verify all visible cards belong to Twitter/X
        for i in range(count):
            card = visible_cards.nth(i)
            platform_attr = card.get_attribute("data-platform")
            assert platform_attr == "Twitter/X"
