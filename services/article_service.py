import logging
import re

import requests

from bs4 import BeautifulSoup

from models.article import db, Article


logger = logging.getLogger(__name__)


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


MIN_CONTENT_LENGTH = 300


def clean_text(text):
    if not text:
        return None

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def extract_paragraphs(container):
    paragraphs = container.find_all("p")

    text_parts = []
    seen = set()

    for paragraph in paragraphs:
        text = clean_text(
            paragraph.get_text(
                " ",
                strip=True,
            )
        )

        if not text:
            continue

        # Ignore extremely short fragments that are unlikely
        # to represent meaningful article prose.
        if len(text) < 25:
            continue

        # Avoid duplicate paragraphs.
        if text in seen:
            continue

        seen.add(text)
        text_parts.append(text)

    if not text_parts:
        return None

    return "\n".join(text_parts)


def extract_article_content(html):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # Remove obvious non-content elements before extraction.
    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "form",
            "nav",
            "footer",
            "aside",
        ]
    ):
        tag.decompose()

    # Prefer semantic article containers first.
    candidate_selectors = [
        "article",
        "main",
        "[role='main']",
        ".article-content",
        ".article-body",
        ".post-content",
        ".post-body",
        ".entry-content",
        ".story-body",
        ".story-content",
    ]

    for selector in candidate_selectors:
        container = soup.select_one(
            selector
        )

        if container is None:
            continue

        content = extract_paragraphs(
            container
        )

        if (
            content
            and len(content) >= MIN_CONTENT_LENGTH
        ):
            return content

    # Fallback:
    # if no useful article-specific container was found,
    # inspect paragraphs across the whole document.
    content = extract_paragraphs(
        soup
    )

    if (
        content
        and len(content) >= MIN_CONTENT_LENGTH
    ):
        return content

    return None


def fetch_article_content(url):
    try:
        response = requests.get(
            url,
            timeout=15,
            headers=REQUEST_HEADERS,
            allow_redirects=True,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        logger.warning(
            "Could not fetch article content: %s (%s)",
            url,
            exc,
        )

        return None

    content_type = response.headers.get(
        "Content-Type",
        "",
    ).lower()

    if (
        content_type
        and "html" not in content_type
    ):
        logger.warning(
            "Article URL did not return HTML: %s",
            url,
        )

        return None

    content = extract_article_content(
        response.text
    )

    if not content:
        logger.warning(
            "Could not extract useful article content: %s",
            url,
        )

        return None

    return content


def populate_article_content(article):
    if article.content:
        return article.content

    content = fetch_article_content(
        article.url
    )

    if content is None:
        return None

    article.content = content

    db.session.commit()

    return content


def populate_missing_article_content(
    limit=10,
):
    articles = Article.query.filter(
        Article.content.is_(None)
    ).limit(
        limit
    ).all()

    populated_count = 0

    for article in articles:
        content = populate_article_content(
            article
        )

        if content:
            populated_count += 1

    return populated_count