import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_SRC = os.path.join(ROOT, "app", "src")
if APP_SRC not in sys.path:
    sys.path.insert(0, APP_SRC)

UI_PATH = os.path.join(APP_SRC, "itsm_agents", "ui_streamlit.py")

if __name__ == "__main__":
    subprocess.run(["streamlit", "run", UI_PATH], check=False)