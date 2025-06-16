import subprocess
import os

def find_and_kill_process_on_port(port):
    try:
        command = f"sudo lsof -t -i :{port}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0 and result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), 15)

                    if os.path.exists(f"/proc/{pid}"):
                        os.kill(int(pid), 9)
                except ProcessLookupError:
                    pass
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    except Exception:
        pass

if __name__ == "__main__":
    ports_to_check = [5001, 5000]

    for port in ports_to_check:
        find_and_kill_process_on_port(port)

    for port in ports_to_check:
        try:
            command = f"sudo lsof -i :{port}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.stdout:
                pass
            else:
                pass
        except Exception:
            pass
