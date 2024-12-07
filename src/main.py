import subprocess
import sys
from utils.utils import *

if __name__ == "__main__":
    config = load_config("../config.yaml")
    print("Configuration loaded")

    now = datetime.now().timestamp()
    start_time = get_time(config['start_time']).timestamp()

    if start_time < now:
        raise ValueError(f"Invalid start time {config['start_time']}\nPlease update the configuration file")

    nodes = config['nodes']
    for node in nodes:
        command = [
            sys.executable,
            "node.py",
            "--id", str(node['id']),
        ]
        node_title = f"Node {node['ip']}:{node['port']}"
        if sys.platform == "win32":
            subprocess.Popen(["start", "cmd", "/K", f"title {node_title} &&"] + command, shell=True)
        elif sys.platform == "darwin":
            apple_script_command = f'''osascript -e 'tell application "Terminal" to do script "{" ".join(command)}"' '''
            subprocess.Popen(apple_script_command, shell=True)
        else:
            subprocess.Popen(["gnome-terminal", "--title", node_title, "--"] + command)

        print(f"Node {node['id']} started on terminal {node['ip']}:{node['port']}")