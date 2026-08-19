import requests

from bs4 import BeautifulSoup

from models.article import db, Article

def fetch_article_content(url):
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )

        response.raise_for_status()

    except requests.RequestException:
        return None

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    paragraphs = soup.find_all("p")

    text_parts = []

    for paragraph in paragraphs:
        text = paragraph.get_text(
            " ",
            strip=True,
        )

        if text:
            text_parts.append(text)

    content = "\n".join(text_parts)

    if not content:
        return None

    return content

def populate_article_content(article):
    if article.content:
        return article.content

    content = fetch_article_content(article.url)

    if content is None:
        return None

    article.content = content
    db.session.commit()

    return content

def populate_missing_article_content(limit=10):
    articles = Article.query.filter(
        Article.content.is_(None)
    ).limit(limit).all()

    populated_count = 0

    for article in articles:
        content = populate_article_content(article)

        if content:
            populated_count += 1

    return populated_count

