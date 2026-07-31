import subprocess
import sys
import time
import urllib.request
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def wait_for_api(url="http://127.0.0.1:8000/health", timeout=15):
    """Polls the FastAPI health endpoint until it is ready."""
    start_time = time.time()
    print("⏳ Waiting for Agentic AI CRM FastAPI Backend Proxy on port 8000...")
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    print("✅ Agentic AI CRM FastAPI Backend Proxy is ONLINE and healthy!")
                    return True
        except Exception:
            time.sleep(0.5)
    print("❌ Timed out waiting for FastAPI to start.")
    return False

def main():
    print("--------------------------------------------------")
    print("🛡️  Starting Agentic AI CRM Assistant with Permission Proxy...")
    print("--------------------------------------------------")

    # 1. Start FastAPI backend subprocess (backend/main.py)
    api_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--port", "8000"]
    api_process = subprocess.Popen(api_cmd)

    try:
        # 2. Wait for API server to become ready
        if not wait_for_api():
            print("Stopping API process...")
            api_process.terminate()
            sys.exit(1)

        print("\n🚀 Launching Streamlit UI Dashboard on http://localhost:8501...")
        print("💡 Press CTRL+C at any time to stop both servers.\n")

        # 3. Start Streamlit dashboard (frontend/app.py)
        dashboard_cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port=8501"]
        subprocess.run(dashboard_cmd)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Agentic AI CRM servers...")
    finally:
        api_process.terminate()
        api_process.wait()
        print("👋 System shutdown complete.")

if __name__ == "__main__":
    main()
