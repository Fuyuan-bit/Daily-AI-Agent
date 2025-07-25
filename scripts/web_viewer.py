from flask import Flask, render_template, abort
import os
import json
from datetime import datetime
from markdown import markdown

# Define the base directory of the project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)

@app.route('/')
def index():
    if not os.path.exists(PROCESSED_DIR):
        return "处理过的数据目录不存在，请先运行 `python main.py run` 来生成简报。", 404

    digests = [f for f in os.listdir(PROCESSED_DIR) 
              if f.endswith(".json")]
    
    # 读取所有简报信息
    digest_list = []
    for digest_file in sorted(digests, reverse=True):
        try:
            with open(os.path.join(PROCESSED_DIR, digest_file), "r", encoding="utf-8") as f:
                data = json.load(f)
                date_str = data['date']
                formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y年%m月%d日")
                digest_list.append({
                    "filename": digest_file,
                    "date": formatted_date,
                    "hot_topics": data.get('hot_topics', [])
                })
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error processing {digest_file}: {e}")

    return render_template('index.html', digests=digest_list)

@app.route('/view/<filename>')
def view_digest(filename):
    file_path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(file_path):
        abort(404)
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Convert the main digest content from Markdown to HTML
    data['digest_html'] = markdown(data.get('digest', ''))

    # The raw articles are now under 'articles_by_topic'
    data['articles_by_topic'] = data.get('articles_by_topic', {})
    
    return render_template('digest.html', digest=data)

def start_web_server():
    """启动Flask Web服务器"""
    app.run(debug=True, port=5000)

if __name__ == '__main__':
    start_web_server()