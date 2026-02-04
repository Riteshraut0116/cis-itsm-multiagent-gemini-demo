import os
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_SRC = os.path.join(ROOT, "app", "src")
UI_PATH = os.path.join(APP_SRC, "itsm_agents", "ui_streamlit.py")

if __name__ == "__main__":
    env = os.environ.copy()

    # Make app/src discoverable for Streamlit subprocess
    env["PYTHONPATH"] = APP_SRC + os.pathsep + env.get("PYTHONPATH", "")

    subprocess.run(["streamlit", "run", UI_PATH], env=env, check=False)