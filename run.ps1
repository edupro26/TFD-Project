$pythonPath = "python"
$scriptPath = "./src/main.py"
$instances = 5
$epoch_duration = 2

for ($i = 1; $i -le $instances; $i++) {
    Start-Process -FilePath $pythonPath -ArgumentList "$scriptPath --node-id $i --epoch-duration $epoch_duration --total-nodes $instances"
}

Write-Output "Started $instances instances."
