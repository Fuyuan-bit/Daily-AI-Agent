import argparse
import os
import sys

# Ensure the scripts directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.processor import save_daily_digest
from scripts.scheduler import start_scheduler
from scripts.view_digest import list_digests
from scripts.web_viewer import start_web_server

def main():
    parser = argparse.ArgumentParser(
        description="每日AI热点助手 - 一个用于抓取、处理和展示AI热点新闻的工具。"
    )
    
    parser.add_argument(
        "action",
        choices=["run", "schedule", "view", "web"],
        help="""
        要执行的操作:
        'run':      手动生成一次今天的AI热点简报。
        'schedule': 启动定时任务，每天自动生成简报。
        'view':     在命令行中查看已生成的历史简报。
        'web':      启动一个本地Web服务器，通过浏览器查看简报。
        """
    )

    args = parser.parse_args()

    # Create data directories if they don't exist
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    if args.action == "run":
        print("正在手动生成今日AI热点简报...")
        save_daily_digest()
    elif args.action == "schedule":
        start_scheduler()
    elif args.action == "view":
        list_digests()
    elif args.action == "web":
        print("正在生成最新的简报，然后启动Web查看器...")
        save_daily_digest()
        print("简报生成完毕。正在启动Web查看器... 请在浏览器中打开 http://127.0.0.1:5000")
        start_web_server()

if __name__ == "__main__":
    main() 