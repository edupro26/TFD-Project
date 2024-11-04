$pythonPath = "python"
$scriptPath = "./src/main.py"
$instances = 5
$epoch_delay = 2

for ($i = 0; $i -le ($instances -1); $i++) {
    Start-Process -FilePath $pythonPath -ArgumentList "$scriptPath --node-id $i --epoch-delay $epoch_delay --total-nodes $instances"
    Start-Sleep -Seconds 1
}

Write-Output "Started $instances instances."