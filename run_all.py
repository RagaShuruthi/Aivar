import subprocess
import sys
import time
import urllib.request
import os

def wait_for_api(url="http://127.0.0.1:8000/health", timeout=15):
    """Polls the FastAPI health endpoint until it is ready."""
    start_time = time.time()
    print("⏳ Waiting for FastAPI Backend Proxy to start on port 8000...")
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    print("✅ FastAPI Backend Proxy is ONLINE and healthy!")
                    return True
        except Exception:
            time.sleep(0.5)
    print("❌ Timed out waiting for FastAPI to start.")
    return False

def main():
    print("--------------------------------------------------")
    print("🛡️  Starting Tool Permission Enforcer System...")
    print("--------------------------------------------------")

    # 1. Start FastAPI backend subprocess
    api_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"]
    api_process = subprocess.Popen(api_cmd)

    try:
        # 2. Wait for API server to become ready
        if not wait_for_api():
            print("Stopping API process...")
            api_process.terminate()
            sys.exit(1)

        print("\n🚀 Launching Streamlit Dashboard on http://localhost:8501...")
        print("💡 Press CTRL+C at any time to stop both servers.\n")

        # 3. Start Streamlit dashboard (runs in foreground)
        dashboard_cmd = [sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port=8501"]
        subprocess.run(dashboard_cmd)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Tool Permission Enforcer servers...")
    finally:
        api_process.terminate()
        api_process.wait()
        print("👋 System shutdown complete.")

if __name__ == "__main__":
    main()
