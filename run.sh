#!/bin/bash

script_path="./src/main.py"
instances=5
epoch_delay=2

for ((i=1; i<=instances; i++)); do
    python "$script_path" --node-id "$i" --epoch-delay "$epoch_delay" --total-nodes "$instances" &
done

echo "Started $instances instances."
