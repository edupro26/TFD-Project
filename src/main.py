import subprocess
import sys

from utils.utils import load_config

if __name__ == "__main__":
    config = load_config("./config.yaml")
    print("Configuration loaded")

    nodes = config['nodes']
    epoch_duration = config['epoch_duration']
    for node in nodes:
        command = [
            sys.executable,
            "node.py",
            "--id", str(node['id']),
            "--host", node['ip'],
            "--port", str(node['port']),
            "--epoch-duration", str(epoch_duration),
            "--peers",
        ] + [f"{peer['ip']}:{peer['port']}" for peer in nodes if peer['id'] != node['id']]

        node_title = f"Node {node['ip']}:{node['port']}"
        if sys.platform == "win32":
            subprocess.Popen(["start", "cmd", "/K", f"title {node_title} &&"] + command, shell=True)
        elif sys.platform == "darwin":
            apple_script_command = f'''osascript -e 'tell application "Terminal" to do script "{" ".join(command)}"' '''
            subprocess.Popen(apple_script_command, shell=True)
        else:
            subprocess.Popen(["gnome-terminal", "--title", node_title, "--"] + command)

        print(f"Node {node['id']} started on terminal {node['ip']}:{node['port']}")