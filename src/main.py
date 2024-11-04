import socket
import subprocess
import sys
import time

from message import Message, MessageType
from transaction import Transaction


def spawn_nodes(base_port, num_nodes, epoch_duration):
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


if __name__ == "__main__":
    base_port = 8000
    n = input("Enter the number of nodes: ")
    epoch = input("Enter the epoch duration: ")

    spawn_nodes(base_port, int(n), int(epoch))
    print("Nodes started\n")

    # Start workload
    print("Running workload...")
    time.sleep(int(n))

    # This is a test message
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(("localhost", base_port))
    tx1 = Transaction(sender=3, receiver=5, tx_id=1111, amount=100)
    msg1 = Message(type=MessageType.ECHO, content=tx1, sender=1)
    sock1.sendall(msg1.serialize())
    sock1.close()

    # This is a test message
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(("localhost", base_port + 1))
    tx2 = Transaction(sender=2, receiver=6, tx_id=2222, amount=200)
    msg2 = Message(type=MessageType.ECHO, content=tx2, sender=2)
    sock2.sendall(msg2.serialize())
    sock2.close()