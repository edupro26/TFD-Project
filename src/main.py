from utils.workload import run_workload
from utils.start_nodes import start_nodes
from utils.args import get_command_line_args

def main():
    BASE_PORT = 8000
    num_nodes, epoch_duration = get_command_line_args()
    start_nodes(BASE_PORT, num_nodes, epoch_duration)
    print("Nodes started\n")
    run_workload()

if __name__ == "__main__":
    main()