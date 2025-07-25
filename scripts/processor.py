from collector import fetch_rss_feeds
import json
import os
from datetime import datetime
import openai
from dotenv import load_dotenv
from collections import Counter
import re

# Define the base directory of the project and paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
ENV_PATH = os.path.join(BASE_DIR, 'config', '.env')

load_dotenv(dotenv_path=ENV_PATH)


def process_articles():
    """处理文章：按主题去重、排序、提取关键信息"""
    articles_by_topic = fetch_rss_feeds()
    processed_articles = {}
    
    for topic, articles in articles_by_topic.items():
        # 1. 基于标题的简单去重
        seen_titles = set()
        unique_articles = []
        for article in articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                unique_articles.append(article)
        
        # 2. 按发布时间排序（新到旧）
        sorted_articles = sorted(unique_articles, 
                               key=lambda x: x['published'], 
                               reverse=True)
        
        processed_articles[topic] = sorted_articles[:10]  # 每个主题最多保留10条
    
    return processed_articles

def identify_hot_topics(articles_by_topic):
    """识别热点话题（简单实现）"""
    all_articles = [article for articles in articles_by_topic.values() for article in articles]
    # 常见AI关键词
    ai_keywords = [
        '大模型', 'LLM', 'GPT', 'Transformer', 'Agent', '扩散模型', 
        '多模态', '强化学习', 'NLP', '计算机视觉', 'AIGC'
    ]
    
    # 统计关键词出现频率
    keyword_counts = Counter()
    for article in all_articles:
        for keyword in ai_keywords:
            if keyword in article['title'] or keyword in article['summary']:
                keyword_counts[keyword] += 1
    
    # 返回前5个热点话题
    return [item[0] for item in keyword_counts.most_common(5)]

def generate_daily_digest(articles_by_topic, hot_topics):
    """使用AI生成每日简报"""
    
    # 构建按主题分类的新闻列表文本
    topic_sections = []
    for topic, articles in articles_by_topic.items():
        if not articles:
            continue
        
        article_list = "\n".join([
            f"- {a['title']}\n  - 摘要: {a['summary']}\n  - 链接: {a['link']}"
            for a in articles
        ])
        topic_sections.append(f"### {topic}\n{article_list}")

    full_article_text = "\n\n".join(topic_sections)
    
    # 构建提示词
    prompt = f"""
你是一位AI科技领域的资深编辑，请根据以下按主题分类的AI热点新闻，生成一篇结构清晰、内容丰富的中文简报。

要求：
1.  **整体结构**:
    -   首先，输出一个"### 今日AI热点概览"标题。
    -   然后，根据热点话题：`{', '.join(hot_topics)}`，撰写一段约100字的趋势点评和分析。
2.  **分主题报道**:
    -   为每个主题创建一个二级标题 (e.g., `## 国内资讯`)。
    -   在每个主题下，挑选2-3条最重要的新闻进行报道。
    -   每条新闻报道格式为:
        -   `#### [新闻标题]`
        -   一段约50字的摘要，用自己的话术总结，不要直接复制原文摘要。
        -   `[原文链接]([链接])`
3.  **语言风格**: 专业、客观、精炼，便于快速阅读。

---
**新闻源：**

{full_article_text}
---
"""
    
    # 使用DeepSeek API
    client = openai.OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"), 
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    )
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024, # 增加token以容纳更长的简报
        temperature=0.3
    )
    
    return response.choices[0].message.content.strip()

def save_daily_digest():
    """主处理流程：获取、处理、生成、保存"""
    # 1. 获取并处理文章
    articles_by_topic = process_articles()
    
    # 2. 识别热点话题
    hot_topics = identify_hot_topics(articles_by_topic)
    
    # 3. 生成简报
    digest_content = generate_daily_digest(articles_by_topic, hot_topics)
    
    # 4. 格式化为Markdown (现在AI直接生成Markdown，此步骤可简化或移除)
    today = datetime.now().strftime("%Y-%m-%d")
    markdown_content = f"# 每日AI热点（{today}）\n\n{digest_content}"
    
    # 5. 保存到本地
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # 保存Markdown文件
    md_path = os.path.join(PROCESSED_DIR, f"{today}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    # 保存JSON格式（便于其他程序处理）
    json_path = os.path.join(PROCESSED_DIR, f"{today}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": today,
            "hot_topics": hot_topics,
            "digest": markdown_content, # 保存包含标题的完整Markdown
            "articles_by_topic": articles_by_topic
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 每日AI热点简报已保存至: {md_path}")
    return md_path

if __name__ == "__main__":
    save_daily_digest() 