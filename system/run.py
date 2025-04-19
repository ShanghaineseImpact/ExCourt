from app import create_app, socketio
from app.sync_courtinfo import sync_court_info
import threading
import time

# 创建 Flask 应用
app = create_app()

# 启动同步任务线程
def start_sync_task():
    def run_sync():
        while True:
            try:
                sync_court_info()
            except Exception as e:
                print(f"Sync task encountered an error: {e}")
                time.sleep(30)  # 等待一段时间后重启任务
            else:
                time.sleep(5)

    sync_thread = threading.Thread(target=run_sync, daemon=True)
    sync_thread.start()

if __name__ == '__main__':
    start_sync_task()  # 启动后台同步任务
    socketio.run(app, host="0.0.0.0", port=8000, debug=False)
