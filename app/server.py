"""
Flask Web Application for Social Media Dashboard.
Exposes web pages for testing along with REST APIs.
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from app.database import init_db, DB_FILE
from app.models import UserModel, PostModel, MetricsModel, AuditModel

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "social_media_dashboard_secret_key_2026")


@app.before_request
def ensure_db():
    if not DB_FILE.exists():
        init_db(DB_FILE, seed=True)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "Social Media Dashboard"}), 200


@app.route("/", methods=["GET"])
def root():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Handle both form post and json
        data = request.form if request.form else request.get_json() or {}
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        if not username or not password:
            error_msg = "Please enter both username and password."
            if request.is_json:
                return jsonify({"success": False, "message": error_msg}), 400
            flash(error_msg, "error")
            return render_template("login.html", error=error_msg), 400

        user = UserModel.authenticate(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            AuditModel.log(user["id"], "USER_LOGIN", f"User {username} logged in successfully")

            if request.is_json:
                return jsonify({"success": True, "redirect": url_for("dashboard")}), 200
            return redirect(url_for("dashboard"))
        else:
            AuditModel.log(None, "LOGIN_FAILED", f"Failed login attempt for {username}")
            error_msg = "Invalid username or password. Please try again."
            if request.is_json:
                return jsonify({"success": False, "message": error_msg}), 401
            flash(error_msg, "error")
            return render_template("login.html", error=error_msg), 401

    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    user_id = session.get("user_id")
    username = session.get("username", "Unknown")
    if user_id:
        AuditModel.log(user_id, "USER_LOGOUT", f"User {username} logged out")
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    metrics = MetricsModel.get_by_user(user_id)
    posts = PostModel.get_all()

    return render_template(
        "dashboard.html",
        active_tab="dashboard",
        user=session,
        metrics=metrics,
        posts=posts
    )


@app.route("/navigation/<view_name>", methods=["GET"])
def navigate_view(view_name):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    metrics = MetricsModel.get_by_user(user_id)
    posts = PostModel.get_all()

    valid_views = ["dashboard", "posts", "analytics", "settings"]
    active_tab = view_name if view_name in valid_views else "dashboard"

    return render_template(
        "dashboard.html",
        active_tab=active_tab,
        user=session,
        metrics=metrics,
        posts=posts
    )


# ================= REST APIs =================

@app.route("/api/posts", methods=["GET", "POST"])
def api_posts():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]

    if request.method == "GET":
        platform = request.args.get("platform", "All")
        posts = PostModel.get_all(platform=platform)
        return jsonify({"posts": posts}), 200

    if request.method == "POST":
        data = request.get_json() or {}
        content = (data.get("content") or "").strip()
        platform = (data.get("platform") or "Twitter/X").strip()
        media_url = (data.get("media_url") or "").strip() or None

        if not content:
            return jsonify({"error": "Post content cannot be empty."}), 400

        if len(content) > 280:
            return jsonify({"error": "Post content exceeds maximum 280 characters limit."}), 400

        post_id = PostModel.create(user_id, platform, content, media_url)
        all_posts = PostModel.get_all()
        updated_metrics = MetricsModel.get_by_user(user_id)

        return jsonify({
            "message": "Post published successfully!",
            "post_id": post_id,
            "posts": all_posts,
            "metrics": updated_metrics
        }), 201


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def api_delete_post(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    success = PostModel.delete(post_id, user_id)
    if success:
        updated_metrics = MetricsModel.get_by_user(user_id)
        return jsonify({
            "message": "Post deleted successfully.",
            "metrics": updated_metrics
        }), 200
    return jsonify({"error": "Post not found or unauthorized to delete."}), 404


@app.route("/api/posts/<int:post_id>/like", methods=["POST"])
def api_like_post(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    likes = PostModel.like(post_id)
    if likes is not None:
        return jsonify({"message": "Post liked!", "likes_count": likes}), 200
    return jsonify({"error": "Post not found."}), 404


@app.route("/api/metrics", methods=["GET"])
def api_metrics():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    metrics = MetricsModel.get_by_user(user_id)
    return jsonify({"metrics": metrics}), 200


def run_server(host="127.0.0.1", port=5000, debug=False):
    init_db(DB_FILE, seed=True)
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    run_server(host="127.0.0.1", port=port, debug=True)
