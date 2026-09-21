"""
Unified CLI Test Runner for Social Media Dashboard Automation Framework.
Allows executing test suites, specific markers, headed mode, or running the standalone web app.
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent


def parse_args():
    parser = argparse.ArgumentParser(description="Social Media Dashboard Test Runner")
    parser.add_argument(
        "-m", "--marker",
        type=str,
        default="",
        help="Run tests matching specific pytest marker (e.g., 'smoke', 'regression', 'db', 'auth', 'posts')"
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run tests in headed browser mode (visible UI)"
    )
    parser.add_argument(
        "-b", "--browser",
        type=str,
        default="chromium",
        choices=["chromium", "firefox", "webkit"],
        help="Target browser for test execution (default: chromium)"
    )
    parser.add_argument(
        "-k", "--keyword",
        type=str,
        default="",
        help="Run tests matching given keyword expression"
    )
    parser.add_argument(
        "--app-only",
        action="store_true",
        help="Start only the web application under test for manual inspection"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.app_only:
        print("\n=======================================================")
        print("  Starting Social Media Dashboard (App Under Test)...")
        print("  Open your browser at: http://127.0.0.1:5000")
        print("=======================================================\n")
        from app.server import run_server
        run_server(host="127.0.0.1", port=5000, debug=True)
        return

    # Set environment variables for test configuration
    env = os.environ.copy()
    env["HEADLESS"] = "false" if args.headed else "true"
    env["BROWSER_TYPE"] = args.browser

    # Build pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--html=reports/report.html",
        "--self-contained-html"
    ]

    if args.marker:
        cmd.extend(["-m", args.marker])

    if args.keyword:
        cmd.extend(["-k", args.keyword])

    print("\n=======================================================")
    print("  SocialPulse Automation Framework Execution")
    print(f"  Browser:  {args.browser}")
    print(f"  Headless: {not args.headed}")
    if args.marker:
        print(f"  Marker:   {args.marker}")
    print("=======================================================\n")

    result = subprocess.run(cmd, cwd=str(WORKSPACE), env=env)

    print("\n=======================================================")
    if result.returncode == 0:
        print("  [SUCCESS] All tests passed successfully!")
    else:
        print(f"  [FAILURE] Test suite exited with return code: {result.returncode}")
    print(f"  [REPORT] Test Report available at: {WORKSPACE / 'reports' / 'report.html'}")
    print("=======================================================\n")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
