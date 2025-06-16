import subprocess

if __name__ == "__main__":
   # subprocess.Popen(["uvicorn", "server_app:app", "--reload", "--host", "0.0.0.0", "--port", "5001"])
    subprocess.Popen(["uvicorn", "server_reminder:app", "--reload", "--host", "0.0.0.0", "--port", "5000"])
