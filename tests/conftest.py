"""
Pytest Fixtures and Hooks for the Social Media Dashboard Automation Framework.
Handles test server lifecycle, Playwright browser management, DB seeding,
and HTML reporting hooks with failure screenshots.
"""

import os
import sys
import time
import socket
import threading
import urllib.request
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from framework.config.config import (
    BASE_URL,
    HEADLESS,
    BROWSER_TYPE,
    SLOW_MO,
    SCREENSHOTS_DIR,
    DB_PATH
)
from framework.utils.db_helper import DatabaseHelper
from framework.utils.logger import get_logger
from app.server import app, run_server

logger = get_logger("Conftest")


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_for_server_health(url: str, timeout_sec: int = 10) -> bool:
    start_time = time.time()
    health_url = f"{url.rstrip('/')}/api/health"
    while time.time() - start_time < timeout_sec:
        try:
            with urllib.request.urlopen(health_url, timeout=1) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


@pytest.fixture(scope="session", autouse=True)
def test_server():
    """Spawns the test web server in a daemon background thread if not already running."""
    db_helper = DatabaseHelper(DB_PATH)
    db_helper.reset_database()

    port = 5000
    if not is_port_in_use(port):
        logger.info(f"Starting embedded Flask test server on port {port}...")
        server_thread = threading.Thread(
            target=run_server,
            kwargs={"host": "127.0.0.1", "port": port, "debug": False},
            daemon=True
        )
        server_thread.start()

        if not wait_for_server_health(BASE_URL, timeout_sec=10):
            raise RuntimeError(f"Server at {BASE_URL} failed health check within 10s.")
        logger.info("Test server is live and healthy.")
    else:
        logger.info(f"Server is already running on port {port}.")

    yield

    logger.info("Test session completed.")


@pytest.fixture(scope="session")
def db_helper():
    """Provides a session-wide DatabaseHelper instance."""
    helper = DatabaseHelper(DB_PATH)
    return helper


@pytest.fixture(scope="function")
def reset_db(db_helper):
    """Fixture to ensure a pristine database state for a specific test function."""
    db_helper.reset_database()
    yield db_helper


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    launch_args = ["--no-sandbox", "--disable-dev-shm-usage"]
    logger.info(f"Launching {BROWSER_TYPE} browser (headless={HEADLESS})")

    if BROWSER_TYPE == "chromium":
        browser = playwright_instance.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO,
            args=launch_args
        )
    elif BROWSER_TYPE == "firefox":
        browser = playwright_instance.firefox.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO,
            args=launch_args
        )
    elif BROWSER_TYPE == "webkit":
        browser = playwright_instance.webkit.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO,
            args=launch_args
        )
    else:
        raise ValueError(f"Unsupported browser type: {BROWSER_TYPE}")

    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        ignore_https_errors=True
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context, request):
    page = context.new_page()
    page.set_default_timeout(10000)

    yield page

    # Screenshot on test failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        test_name = request.node.name.replace("/", "_").replace("\\", "_")
        screenshot_path = SCREENSHOTS_DIR / f"FAIL_{test_name}.png"
        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
            logger.error(f"Test failed! Screenshot captured at: {screenshot_path}")
        except Exception as e:
            logger.warning(f"Could not capture failure screenshot: {e}")

    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Stores test outcome on the request.node for the page fixture to access."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_html_report_title(report):
    report.title = "SocialPulse Test Automation Execution Report"
