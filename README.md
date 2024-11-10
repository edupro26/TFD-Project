# Distributed Fault Tolerance | Project - Phase 1 | 2024/2025

### Blockchain implementation following a Streamlet consensus algorithm

This project is being developed for the Distributed Fault Tolerance 
course of the Master's degree in Computer Science at the Faculty 
of Sciences of the University of Lisbon.

### Authors

Group 12:

- Eduardo Proença nº57551
- Pedro Cardoso nº58212
- Ricardo Costa nº64371


## Overview

This repository contains the code for the first phase of a blockchain implementation
following a Streamlet consensus algorithm. This protocol operates under partial synchrony, 
tolerating faults and node crashes without compromising the blockchain’s integrity. It 
allows nodes to propose, vote, and finalize blocks in the blockchain, ensuring that the
blockchain remains consistent and synchronized across all nodes.

### Functionalities

- **P2P communication**
- **Propose-Vote**
- **Echoing**
- **Block Notarization**
- **Blockchain Finalization**
- **Fault Tolerance**

Next steps for phase 2 include, implementing better fault tolerance mechanisms to deal with
delaying of nodes, lost epochs and node crashes.

### Source code organization

- `domain`: This directory contains data strutctures used to maintain the blockchain
- `utils`: This directory contains utility functions and scripts
- `node.py`: Node class that represents a node in the network
- `main.py`: Main script that launches the blockchain

**Note**: In the `docs` directory, you can find more documentation.

## Usage

**Note**: We recommend you to have Python 3.10 or higher installed.

To run the blockchain, you need to execute the `main.py` script: (Found in the `src` folder)

```python main.py```

This script will ask you for a number of nodes to create and an epoch duration in seconds. 
After that, it will start the nodes, each in a separate terminal, and run a workload
simulating clients submitting transactions to the network. </br>
Then, you can look at the node terminals to see the blockchain being built and finalized.

An execution example is shown below:

```
$ python main.py
Enter the number of nodes: 5
Enter the epoch duration: 2
Nodes started

Running workload...
```

If you wish, it is also possible to run each node separately. To do so, you can run
the following command to start a node: (this command only starts one node)

```python node.py --id <id> --epoch-duration <epoch-duration> --port <port> --peers <peers>```

After all the nodes are up, you can then start the workload by running:

```python workload.py --base-port <base-port> --num-nodes <num-nodes>```

**Note**: Keep in mind that all scripts must be executed in diferent terminals.