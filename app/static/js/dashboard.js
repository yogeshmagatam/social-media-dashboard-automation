/**
 * SocialPulse Dashboard Client Interactions
 * Handles dynamic feed updates, metrics refresh, post creations, deletions, and likes.
 */

document.addEventListener("DOMContentLoaded", () => {
    initCharCounter();
    initPostCreation();
    initFeedActions();
    initPlatformFilter();
});

function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = "fa-circle-info";
    if (type === "success") icon = "fa-circle-check";
    if (type === "error") icon = "fa-circle-exclamation";

    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function initCharCounter() {
    const textarea = document.getElementById("post-content");
    const counter = document.getElementById("char-counter");

    if (textarea && counter) {
        textarea.addEventListener("input", () => {
            const length = textarea.value.length;
            counter.textContent = `${length} / 280`;
            if (length > 250) {
                counter.style.color = "var(--accent-orange)";
            } else {
                counter.style.color = "var(--text-muted)";
            }
        });
    }
}

function initPostCreation() {
    const form = document.getElementById("create-post-form");
    const contentInput = document.getElementById("post-content");
    const platformInput = document.getElementById("post-platform");
    const mediaInput = document.getElementById("post-media-url");
    const errorBanner = document.getElementById("post-validation-error");

    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const content = (contentInput.value || "").trim();
        const platform = platformInput.value;
        const media_url = mediaInput ? mediaInput.value.trim() : "";

        // Client-side validation
        if (!content) {
            if (errorBanner) {
                errorBanner.textContent = "Post content cannot be empty.";
                errorBanner.classList.remove("hidden");
            }
            showToast("Please enter some post content.", "error");
            return;
        }

        if (content.length > 280) {
            if (errorBanner) {
                errorBanner.textContent = "Post content exceeds 280 characters.";
                errorBanner.classList.remove("hidden");
            }
            showToast("Content exceeds 280 characters limit.", "error");
            return;
        }

        if (errorBanner) {
            errorBanner.classList.add("hidden");
        }

        try {
            const response = await fetch("/api/posts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ platform, content, media_url })
            });

            const data = await response.json();

            if (response.ok) {
                showToast("Post published successfully!", "success");
                form.reset();
                const counter = document.getElementById("char-counter");
                if (counter) counter.textContent = "0 / 280";

                // Update metric counters if available
                if (data.metrics) {
                    updateMetricsUI(data.metrics);
                }

                // Prepend new post to the feed
                renderPosts(data.posts);
            } else {
                showToast(data.error || "Failed to publish post.", "error");
                if (errorBanner) {
                    errorBanner.textContent = data.error || "Failed to publish post.";
                    errorBanner.classList.remove("hidden");
                }
            }
        } catch (err) {
            console.error("Post creation error:", err);
            showToast("Network error creating post.", "error");
        }
    });
}

function initFeedActions() {
    const feed = document.getElementById("posts-list");
    if (!feed) return;

    feed.addEventListener("click", async (e) => {
        // Delete post
        const deleteBtn = e.target.closest(".delete-post-btn");
        if (deleteBtn) {
            const postId = deleteBtn.getAttribute("data-id");
            if (confirm("Are you sure you want to delete this post?")) {
                await deletePost(postId);
            }
            return;
        }

        // Like post
        const likeBtn = e.target.closest(".like-post-btn");
        if (likeBtn) {
            const postId = likeBtn.getAttribute("data-id");
            await likePost(postId, likeBtn);
            return;
        }
    });
}

async function deletePost(postId) {
    try {
        const response = await fetch(`/api/posts/${postId}`, { method: "DELETE" });
        const data = await response.json();

        if (response.ok) {
            showToast("Post deleted.", "info");
            const postCard = document.getElementById(`post-${postId}`);
            if (postCard) {
                postCard.remove();
            }
            if (data.metrics) {
                updateMetricsUI(data.metrics);
            }
        } else {
            showToast(data.error || "Failed to delete post.", "error");
        }
    } catch (err) {
        console.error("Delete error:", err);
        showToast("Error deleting post.", "error");
    }
}

async function likePost(postId, button) {
    try {
        const response = await fetch(`/api/posts/${postId}/like`, { method: "POST" });
        const data = await response.json();

        if (response.ok) {
            const countSpan = document.getElementById(`like-count-${postId}`);
            if (countSpan) {
                countSpan.textContent = data.likes_count;
            }
            button.classList.toggle("liked");
            const heartIcon = button.querySelector("i");
            if (heartIcon) {
                heartIcon.classList.toggle("fa-solid");
                heartIcon.classList.toggle("fa-regular");
            }
        }
    } catch (err) {
        console.error("Like error:", err);
    }
}

function initPlatformFilter() {
    const filter = document.getElementById("platform-filter");
    if (!filter) return;

    filter.addEventListener("change", () => {
        const selected = filter.value;
        const posts = document.querySelectorAll(".post-card");

        posts.forEach(post => {
            const postPlatform = post.getAttribute("data-platform");
            if (selected === "All" || postPlatform === selected) {
                post.style.display = "block";
            } else {
                post.style.display = "none";
            }
        });
    });
}

function updateMetricsUI(metrics) {
    const postsMetric = document.getElementById("metric-posts");
    const followersMetric = document.getElementById("metric-followers");
    const impressionsMetric = document.getElementById("metric-impressions");
    const engagementMetric = document.getElementById("metric-engagement");

    if (postsMetric && metrics.total_posts !== undefined) {
        postsMetric.textContent = metrics.total_posts;
    }
    if (followersMetric && metrics.total_followers !== undefined) {
        followersMetric.textContent = metrics.total_followers.toLocaleString();
    }
    if (impressionsMetric && metrics.total_impressions !== undefined) {
        impressionsMetric.textContent = metrics.total_impressions.toLocaleString();
    }
    if (engagementMetric && metrics.engagement_rate !== undefined) {
        engagementMetric.textContent = `${metrics.engagement_rate}%`;
    }
}

function renderPosts(posts) {
    const feed = document.getElementById("posts-list");
    if (!feed) return;

    if (!posts || posts.length === 0) {
        feed.innerHTML = `
            <div class="empty-feed" id="empty-feed-placeholder">
                <i class="fa-solid fa-comments"></i>
                <p>No posts published yet. Create your first post above!</p>
            </div>
        `;
        return;
    }

    feed.innerHTML = posts.map(post => {
        let iconClass = "fa-brands fa-x-twitter";
        const platLower = (post.platform || "").toLowerCase();
        if (platLower.includes("linkedin")) iconClass = "fa-brands fa-linkedin";
        else if (platLower.includes("instagram")) iconClass = "fa-brands fa-instagram";
        else if (platLower.includes("youtube")) iconClass = "fa-brands fa-youtube";

        const platformSlug = platLower.replace("/", "-");

        return `
            <article class="post-card" id="post-${post.id}" data-post-id="${post.id}" data-platform="${post.platform}">
                <div class="post-card-header">
                    <div class="post-meta">
                        <span class="platform-tag platform-${platformSlug}">
                            <i class="${iconClass}"></i>
                            ${post.platform}
                        </span>
                        <span class="post-author">${post.full_name}</span>
                        <span class="post-time">${post.created_at}</span>
                    </div>
                    <button class="delete-post-btn" id="delete-btn-${post.id}" data-id="${post.id}" title="Delete Post">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>

                <div class="post-card-body">
                    <p class="post-content-text">${escapeHtml(post.content)}</p>
                    ${post.media_url ? `
                        <div class="post-media-wrapper">
                            <img src="${escapeHtml(post.media_url)}" alt="Post Media" class="post-media-img" loading="lazy">
                        </div>
                    ` : ""}
                </div>

                <div class="post-card-footer">
                    <button class="like-post-btn" id="like-btn-${post.id}" data-id="${post.id}">
                        <i class="fa-regular fa-heart"></i>
                        <span class="like-count" id="like-count-${post.id}">${post.likes_count}</span>
                    </button>
                    <span class="comments-count">
                        <i class="fa-regular fa-comment"></i> ${post.comments_count}
                    </span>
                </div>
            </article>
        `;
    }).join("");
}

function escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
