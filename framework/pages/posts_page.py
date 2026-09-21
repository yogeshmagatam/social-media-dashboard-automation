"""
Page Object Model for Post Creation, Feed Management, Filtering, Likes, and Deletions.
"""

from playwright.sync_api import Page
from framework.pages.base_page import BasePage
from framework.utils.logger import get_logger

logger = get_logger("PostsPage")


class PostsPage(BasePage):
    # Form Locators
    POST_CONTENT_INPUT = "#post-content"
    POST_PLATFORM_SELECT = "#post-platform"
    POST_MEDIA_URL_INPUT = "#post-media-url"
    SUBMIT_POST_BTN = "#submit-post-btn"
    CHAR_COUNTER = "#char-counter"
    VALIDATION_ERROR = "#post-validation-error"

    # Feed Locators
    PLATFORM_FILTER = "#platform-filter"
    POSTS_LIST = "#posts-list"
    POST_CARDS = ".post-card"
    FIRST_POST_CARD = ".post-card >> nth=0"
    FIRST_POST_CONTENT = ".post-card >> nth=0 >> .post-content-text"
    FIRST_POST_PLATFORM = ".post-card >> nth=0 >> .platform-tag"
    FIRST_POST_LIKE_BTN = ".post-card >> nth=0 >> .like-post-btn"
    FIRST_POST_LIKE_COUNT = ".post-card >> nth=0 >> .like-count"
    FIRST_POST_DELETE_BTN = ".post-card >> nth=0 >> .delete-post-btn"

    def __init__(self, page: Page):
        super().__init__(page)

    def create_post(self, platform: str, content: str, media_url: str = ""):
        """Fills out the post creation form and clicks publish."""
        logger.info(f"Creating post for {platform}: '{content[:30]}...'")
        self.select_option(self.POST_PLATFORM_SELECT, platform)
        self.fill(self.POST_CONTENT_INPUT, content)
        if media_url:
            self.fill(self.POST_MEDIA_URL_INPUT, media_url)
        self.click(self.SUBMIT_POST_BTN)
        # Short wait for DOM insertion or network settle
        self.page.wait_for_timeout(500)

    def get_char_counter_text(self) -> str:
        return self.get_text(self.CHAR_COUNTER)

    def get_validation_error_text(self) -> str:
        if self.is_visible(self.VALIDATION_ERROR, timeout=3000):
            return self.get_text(self.VALIDATION_ERROR)
        return ""

    def get_feed_posts_count(self) -> int:
        """Returns the number of currently visible post cards."""
        self.page.wait_for_selector(self.POSTS_LIST, state="visible", timeout=self.timeout)
        return self.page.locator(self.POST_CARDS).count()

    def get_latest_post_content(self) -> str:
        """Returns the text content of the top post in feed."""
        return self.get_text(self.FIRST_POST_CONTENT)

    def get_latest_post_platform(self) -> str:
        """Returns the platform tag text of the top post."""
        return self.get_text(self.FIRST_POST_PLATFORM)

    def like_latest_post(self) -> int:
        """Clicks like button on latest post and returns updated count."""
        initial_count = int(self.get_text(self.FIRST_POST_LIKE_COUNT))
        self.click(self.FIRST_POST_LIKE_BTN)
        self.page.wait_for_timeout(300)
        updated_count = int(self.get_text(self.FIRST_POST_LIKE_COUNT))
        return updated_count

    def delete_latest_post(self):
        """Clicks delete on top post and accepts dialog."""
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.click(self.FIRST_POST_DELETE_BTN)
        self.page.wait_for_timeout(500)

    def filter_by_platform(self, platform_name: str):
        """Changes the feed platform filter."""
        logger.info(f"Filtering feed by platform: '{platform_name}'")
        self.select_option(self.PLATFORM_FILTER, platform_name)
        self.page.wait_for_timeout(300)

    def get_first_post_id(self) -> str:
        """Retrieves data-post-id attribute of top post."""
        locator = self.page.locator(self.FIRST_POST_CARD)
        return locator.get_attribute("data-post-id") or ""
