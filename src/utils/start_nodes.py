import sys, subprocess

def start_nodes(base_port, num_nodes, epoch_duration):
    for i in range(num_nodes):
        port = base_port + i
        command = [
            sys.executable,
            "node.py",
            "--id", str(i),
            "--epoch-duration", str(epoch_duration),
            "--port", str(port),
            "--peers"
        ] + [str(base_port + j) for j in range(num_nodes) if j != i]

        if sys.platform == "win32":
            subprocess.Popen(["start", "cmd", "/K"] + command, shell=True)
        elif sys.platform == "Linux": # TODO verify if this works on Linux
            subprocess.Popen(["gnome-terminal", "--"] + command)
        else: # TODO verify if this works on MacOS
            apple_script_command = f'''osascript -e 'tell application "Terminal" to do script "{" ".join(command)}"' '''
            subprocess.Popen(apple_script_command, shell=True)