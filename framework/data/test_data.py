"""
Test Datasets for Functional, Negative, and Regression Tests.
Separates test data from test scripts following automation best practices.
"""

# Valid User Credentials
VALID_USER = {
    "username": "testuser",
    "password": "Password@123",
    "full_name": "Sarah Connor",
    "email": "sarah@socialpulse.io",
    "role": "creator"
}

ADMIN_USER = {
    "username": "admin",
    "password": "Admin@123",
    "full_name": "Alex Rivera",
    "email": "alex@socialpulse.io",
    "role": "admin"
}

QA_TESTER = {
    "username": "qa_tester",
    "password": "QASecret#2026",
    "full_name": "David Miller",
    "email": "david@socialpulse.io",
    "role": "tester"
}

# Negative Authentication Test Scenarios
NEGATIVE_LOGIN_CASES = [
    {
        "test_id": "TC_AUTH_01",
        "desc": "Invalid Password",
        "username": "testuser",
        "password": "WrongPassword999!",
        "expected_error": "Invalid username or password"
    },
    {
        "test_id": "TC_AUTH_02",
        "desc": "Non-existent Username",
        "username": "ghost_user_does_not_exist",
        "password": "Password@123",
        "expected_error": "Invalid username or password"
    },
    {
        "test_id": "TC_AUTH_03",
        "desc": "SQL Injection Attempt",
        "username": "' OR '1'='1",
        "password": "' OR '1'='1",
        "expected_error": "Invalid username or password"
    }
]

# Post Management Test Cases
SAMPLE_POSTS = {
    "standard_post": {
        "platform": "Twitter/X",
        "content": "Automated regression testing verified with Playwright & Pytest! All systems green. 🚀 #QA #Automation",
        "media_url": ""
    },
    "linkedin_article": {
        "platform": "LinkedIn",
        "content": "Excited to demonstrate the power of Page Object Model and direct SQL verification in end-to-end web testing.",
        "media_url": ""
    },
    "instagram_photo": {
        "platform": "Instagram",
        "content": "Behind the scenes: Cloud CI/CD pipeline running 50+ Playwright checks in under 30 seconds! ⚡📸",
        "media_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600"
    },
    "youtube_update": {
        "platform": "YouTube",
        "content": "New video drop: Complete Walkthrough of Test Automation Architecture with Python and SQLite.",
        "media_url": ""
    },
    "max_boundary_post": {
        "platform": "Twitter/X",
        "content": "A" * 280,  # Exactly 280 characters
        "media_url": ""
    },
    "exceed_boundary_post": {
        "platform": "Twitter/X",
        "content": "B" * 285,  # 285 characters (exceeds limit)
        "media_url": ""
    }
}
