"""
TruthGuard AI - Platform Launcher
Starts the Uvicorn web server and automatically opens the dashboard in your default browser.
"""

import sys
import time
import webbrowser
import uvicorn

PORT = 8000
HOST = "127.0.0.1"

def open_browser():
    time.sleep(1.2)
    url = f"http://{HOST}:{PORT}"
    print(f"\n=======================================================")
    print(f"🚀 TruthGuard AI is running live at: {url}")
    print(f"💡 Opening your default browser now...")
    print(f"=======================================================\n")
    webbrowser.open(url)

if __name__ == "__main__":
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
