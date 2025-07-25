import schedule
import time
from datetime import datetime
import os
import sys

# Define the base directory of the project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the project root to the Python path
sys.path.append(BASE_DIR)

from scripts.processor import save_daily_digest

def run_daily_digest():
    """执行每日简报生成任务"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始生成每日AI热点简报...")
    try:
        save_daily_digest()
        print(f"✅ 简报生成成功")
    except Exception as e:
        print(f"❌ 简报生成失败: {str(e)}")


def start_scheduler():
    """设置并启动定时任务"""
    # 设置每天早上8:00执行
    schedule.every().day.at("08:00").do(run_daily_digest)
    
    print("每日AI热点Agent已启动，等待执行时间...")
    print("按Ctrl+C停止程序")
    
    # Run once at startup
    print("为了立即看到效果，将在启动时首先执行一次任务。")
    run_daily_digest()

    # 保持程序运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    start_scheduler() 