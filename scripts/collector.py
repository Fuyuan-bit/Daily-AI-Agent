import feedparser
import json
import os
from datetime import datetime, timedelta

# Define the base directory of the project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def fetch_rss_feeds():
    """从配置文件中读取RSS源并按主题抓取内容"""
    config_path = os.path.join(BASE_DIR, 'config', 'rss_sources.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        topics = json.load(f)
    
    all_articles_by_topic = {}
    now = datetime.utcnow()
    
    for topic, sources in topics.items():
        topic_articles = []
        for source in sources:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries:
                # 只获取24小时内的文章
                published = entry.get('published_parsed')
                if published:
                    pub_date = datetime(*published[:6])
                    if now - pub_date < timedelta(hours=24):
                        topic_articles.append({
                            "title": entry.title,
                            "summary": entry.get('summary', '')[:300] + "..." if len(entry.get('summary', '')) > 300 else entry.get('summary', ''),
                            "link": entry.link,
                            "source": source['name'],
                            "published": pub_date.isoformat(),
                            "topic": topic
                        })
        all_articles_by_topic[topic] = topic_articles
    
    # 保存原始数据
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    with open(f"{raw_dir}/raw_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(all_articles_by_topic, f, ensure_ascii=False, indent=2)
    
    return all_articles_by_topic 