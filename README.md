# Distributed Fault Tolerance | Project - Phase 2 | 2024/2025

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

This repository contains the code of a blockchain implementation
following a Streamlet consensus algorithm.

### Source code organization

- `domain`: This directory contains data strutctures used to maintain the blockchain
- `utils`: This directory contains utility functions and scripts
- `node.py`: Node class that represents a node in the network
- `main.py`: Main script that lauches the nodes

### Limitations

Your implemetation does not write the blockchain to disk so, 
in the event of a crash, when the node is recovered despite being able to catch
up to the other nodes, it will not have the blocks that it lost will being down.


## Usage

**Note**: You should have Python 3.12 or higher installed.

To run the blockchain, you need to execute the `main.py` script: (Found in the `src` folder)

```python main.py```

This script will read the configuration file `config.yaml` and set a start time
to lauch the nodes each in a separate terminal. 

When it hits the start time, the nodes will initiate the protocol.

Then, you can look at the node terminals to see the blockchain being built and finalized.

An execution example is shown below:

```
$ python main.py
Configuration file loaded
Start time set to 2024-12-08 19:51:11.368839
Node 0 started on terminal 127.0.0.1:8000
Node 1 started on terminal 127.0.0.1:8001
Node 2 started on terminal 127.0.0.1:8002
```

If you choose to stop a node (crash simulation), you can restart it by running:

```python node.py --id <id>```

**Note:** There needs to be always a majority of nodes 
running for the protocol to function properly. 