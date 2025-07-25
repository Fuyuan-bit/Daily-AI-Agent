import os
from datetime import datetime
import re

# Define the base directory of the project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def list_digests():
    """列出所有已保存的简报"""
    if not os.path.exists(PROCESSED_DIR):
        print("处理过的数据目录不存在，请先运行 `python main.py run` 来生成简报。")
        return

    digests = [f for f in os.listdir(PROCESSED_DIR) 
              if f.endswith(".md")]
    
    if not digests:
        print("没有找到已保存的简报")
        return
    
    print("\n已保存的AI热点简报：")
    sorted_digests = sorted(digests, reverse=True)
    for i, digest in enumerate(sorted_digests, 1):
        date_str = os.path.splitext(digest)[0]
        try:
            formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y年%m月%d日")
            print(f"{i}. {formatted_date} - {digest}")
        except ValueError:
            # Skip files that don't match the date format
            continue
    
    # This part needs adjustment if there are non-date files
    usable_digests = [d for d in sorted_digests if re.match(r'\d{4}-\d{2}-\d{2}\.md', d)]

    # 选择查看
    choice = input("\n输入编号查看简报 (q退出): ")
    if choice.lower() == 'q':
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(usable_digests):
            with open(os.path.join(PROCESSED_DIR, usable_digests[idx]), "r", encoding="utf-8") as f:
                print("\n" + "="*50)
                print(f.read())
                print("="*50)
        else:
            print("无效的编号")
    except ValueError:
        print("请输入有效编号")

if __name__ == "__main__":
    list_digests() 