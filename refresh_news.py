from app import app
from services.news_service import get_vc_articles

with app.app_context():
    articles = get_vc_articles()
    print(f"Refresh complete. Processed {len(articles)} articles.")