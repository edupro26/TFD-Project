import subprocess
import sys


def start_nodes(base_port, num_nodes, epoch_duration):
    """
    Starts the nodes each in a separate terminal
    :param base_port: the base port number
    :param num_nodes: the number of nodes
    :param epoch_duration: the duration of an epoch in seconds
    """
    for i in range(num_nodes):
        port = base_port + i
        node_title = f"Node {i} - Port {port}"
        command = [
            sys.executable,
            "node.py",
            "--id", str(i),
            "--epoch-duration", str(epoch_duration),
            "--port", str(port),
            "--peers"
        ] + [str(base_port + j) for j in range(num_nodes) if j != i]

        if sys.platform == "win32":
            subprocess.Popen(["start", "cmd", "/K", f"title {node_title} &&"] + command, shell=True)
        elif sys.platform == "darwin":
            apple_script_command = f'''osascript -e 'tell application "Terminal" to do script "{" ".join(command)}"' '''
            subprocess.Popen(apple_script_command, shell=True)
        else:
            subprocess.Popen(["gnome-terminal", "--title", node_title, "--"] + command)