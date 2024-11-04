#!/bin/bash

script_path="./src/main.py"
instances=5
epoch_duration=2

for ((i=0; i<=(instances - 1); i++)); do
    python "$script_path" --node-id "$i" --epoch-duration "$epoch_duration" --total-nodes "$instances" &
done

echo "Started $instances instances."